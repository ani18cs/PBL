import unittest
import time
import os
import sys

# Ensure ddos_platform package imports are resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db, get_connection
from detection.detector import DDoSDetector

class TestDDoSDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.detector = DDoSDetector()

    def test_rate_analyzer_thresholds(self):
        # 1. Normal traffic (10 PPS from unique IPs) -> GREEN
        ips = [f"192.168.1.{i}" for i in range(10)]
        sev = self.detector.process_traffic_slice(10, 1, ips)
        self.assertEqual(sev, "GREEN")

        # 2. Suspicious traffic (80 PPS) -> YELLOW
        ips = [f"192.168.1.{i}" for i in range(10, 30)] * 4  # 80 requests, 20 unique IPs
        sev = self.detector.process_traffic_slice(80, 1, ips)
        self.assertEqual(sev, "YELLOW")

        # 3. Critical traffic (200 PPS) -> RED
        sev = self.detector.process_traffic_slice(200, 1, ips)
        self.assertEqual(sev, "RED")

    def test_burst_detection(self):
        detector = DDoSDetector()
        
        # 1. Populate burst history loop with low rates (10 PPS)
        for _ in range(5):
            detector.process_traffic_slice(10, 1, [f"192.168.1.{i}" for i in range(10)])
            
        # 2. Spike from average 10 to 40 (4x multiplier) -> ORANGE alert
        sev = detector.process_traffic_slice(40, 1, [f"192.168.1.{i}" for i in range(10)] * 4)
        self.assertEqual(sev, "ORANGE")

    def test_entropy_anomaly_concentration(self):
        detector = DDoSDetector()
        
        # 1. Targeted single-source flood (30 PPS from single IP) -> RED anomaly
        ips = ["192.168.1.99"] * 30
        sev = detector.process_traffic_slice(30, 2, ips)
        self.assertEqual(sev, "RED")
        
        # 2. Verify alert logged with target IP in database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts WHERE source_ip = '192.168.1.99'")
        rows = cursor.fetchall()
        conn.close()
        self.assertTrue(len(rows) > 0)

if __name__ == '__main__':
    unittest.main()
