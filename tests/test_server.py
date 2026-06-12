import unittest
import socket
import time
import os
import sys

# Ensure ddos_platform package imports are resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db
from server.target_server import TargetServer

class TestTargetServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize database path
        init_db()

    def setUp(self):
        self.server = TargetServer(host="127.0.0.1", port=9999)
        self.server.start()
        # Give server thread time to bind
        time.sleep(0.3)

    def tearDown(self):
        self.server.stop()
        time.sleep(0.3)

    def test_client_connection_and_request(self):
        # 1. Start with 0 active connections
        self.assertEqual(self.server.conn_manager.get_active_count(), 0)

        # 2. Connect client socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 9999))
        time.sleep(0.1)

        # 3. Connection count should be 1
        self.assertEqual(self.server.conn_manager.get_active_count(), 1)

        # 4. Send request and check for ACK response
        client.sendall(b"HELLO\n")
        response = client.recv(1024)
        self.assertEqual(response, b"ACK\n")

        # 5. Send second request
        client.sendall(b"DATA\n")
        response = client.recv(1024)
        self.assertEqual(response, b"ACK\n")

        # 6. Verify counters in conn_manager
        req_count, active_count, avg_lat = self.server.conn_manager.pop_metrics()
        self.assertEqual(req_count, 2)
        self.assertEqual(active_count, 1)
        self.assertTrue(avg_lat > 0.0)

        # 7. Close client connection
        client.close()
        time.sleep(0.1)

        # 8. Active connections count should fall back to 0
        self.assertEqual(self.server.conn_manager.get_active_count(), 0)

if __name__ == '__main__':
    unittest.main()
