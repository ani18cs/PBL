import unittest
import time
import os
import sys

# Ensure ddos_platform package imports are resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db, get_connection
from monitoring.metrics_collector import MetricsCollector

class TestMetricsCollector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_collect_system_metrics(self):
        # 1. Initialize collector with a short 0.2s interval
        collector = MetricsCollector(interval=0.2)
        collector.start()
        
        # 2. Wait to sample data points
        time.sleep(1.0)
        collector.stop()
        
        # 3. Retrieve system_metrics from database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM system_metrics ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        # 4. Verify metric data formats and thresholds
        self.assertTrue(len(rows) >= 2, "Should have recorded at least 2 metrics sets")
        latest = dict(rows[0])
        
        self.assertIn("cpu_usage", latest)
        self.assertIn("memory_usage", latest)
        self.assertIn("disk_usage", latest)
        self.assertIn("network_in", latest)
        self.assertIn("network_out", latest)
        
        self.assertTrue(0.0 <= latest["cpu_usage"] <= 100.0)
        self.assertTrue(0.0 <= latest["memory_usage"] <= 100.0)
        self.assertTrue(0.0 <= latest["disk_usage"] <= 100.0)
        self.assertTrue(latest["network_in"] >= 0.0)
        self.assertTrue(latest["network_out"] >= 0.0)

if __name__ == '__main__':
    unittest.main()
