import unittest
import time
import os
import sys

# Ensure ddos_platform package imports are resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db
from database.models import ExperimentModel
from server.target_server import TargetServer
from simulator.experiment_runner import ExperimentRunner

class TestTrafficSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.server = TargetServer(host="127.0.0.1", port=9998)
        self.server.start()
        self.runner = ExperimentRunner(target_host="127.0.0.1", target_port=9998)
        time.sleep(0.3)

    def tearDown(self):
        self.runner.stop_active_experiment()
        self.server.stop()
        time.sleep(0.3)

    def test_run_normal_experiment(self):
        # 1. Trigger normal profile experiment for 3 seconds
        success = self.runner.run_experiment(
            name="Test Normal Load Run",
            profile_name="normal",
            duration_seconds=3
        )
        self.assertTrue(success)
        self.assertIsNotNone(self.runner.active_experiment_id)

        # 2. Wait to gather metrics
        time.sleep(1.5)
        
        # 3. Verify target server is receiving and registering requests
        req_count, active_count, avg_lat = self.server.conn_manager.pop_metrics()
        self.assertTrue(req_count > 0, "Requests should be registered at server")

        # 4. Wait for duration timer to expire and verify auto-stop
        time.sleep(2.0)
        self.assertIsNone(self.runner.active_experiment_id, "Experiment runner should self-terminate once timer finishes")

        # 5. Check database logging history
        experiments = ExperimentModel.get_all()
        self.assertTrue(len(experiments) > 0)
        latest = experiments[0]
        self.assertEqual(latest["name"], "Test Normal Load Run")
        self.assertIsNotNone(latest["end_time"])

if __name__ == '__main__':
    unittest.main()
