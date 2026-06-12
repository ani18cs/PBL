import unittest
import time
import os
import sys

# Ensure ddos_platform package imports are resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db
from mitigation.mitigation_controller import MitigationController

class TestMitigationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.controller = MitigationController()

    def test_blacklist_manager(self):
        manager = self.controller.blacklist_manager
        ip = "192.168.1.55"
        
        self.assertFalse(manager.is_blocked(ip))
        manager.block_ip(ip, duration_seconds=1)
        self.assertTrue(manager.is_blocked(ip))
        
        # Wait for expiration
        time.sleep(1.2)
        self.assertFalse(manager.is_blocked(ip))

    def test_rate_limiter_sliding_window(self):
        limiter = self.controller.rate_limiter
        limiter.update_limit(3)
        ip = "192.168.1.66"
        
        # 3 requests allowed
        self.assertFalse(limiter.is_rate_limited(ip))
        self.assertFalse(limiter.is_rate_limited(ip))
        self.assertFalse(limiter.is_rate_limited(ip))
        
        # 4th request rate limited
        self.assertTrue(limiter.is_rate_limited(ip))

    def test_connection_concurrency_limiter(self):
        limiter = self.controller.connection_limiter
        limiter.update_limit(2)
        ip = "192.168.1.77"
        
        self.assertTrue(limiter.register_connection(ip))
        self.assertTrue(limiter.register_connection(ip))
        # Exceeds concurrency limit
        self.assertFalse(limiter.register_connection(ip))
        
        # Release one
        limiter.unregister_connection(ip)
        self.assertTrue(limiter.register_connection(ip))

    def test_mitigation_controller_auto_block(self):
        self.controller.set_mode("automatic")
        self.controller.rate_limiter.update_limit(2)
        ip = "10.0.0.99"
        
        # Allow first 2 requests
        self.assertTrue(self.controller.handle_request(ip))
        self.assertTrue(self.controller.handle_request(ip))
        
        # 3rd request fails and triggers automatic block
        self.assertFalse(self.controller.handle_request(ip))
        
        # Future requests blocked immediately by blacklist
        self.assertTrue(self.controller.blacklist_manager.is_blocked(ip))

if __name__ == '__main__':
    unittest.main()
