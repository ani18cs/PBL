import unittest
import os
import sys
import time

# Ensure ddos_platform package imports are resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db
from database.models import ExperimentModel, SystemMetricsModel, TrafficMetricsModel, AlertModel, MitigationActionModel
from analytics.report_generator import generate_pdf_report

class TestReportGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_report_compilation(self):
        # 1. Start a mock experiment in SQLite
        exp_id = ExperimentModel.start_experiment(
            "Integration Test Simulation Report",
            {"profile": "heavy", "duration": 30, "clients": 80, "request_interval": 0.05, "concurrency": 15}
        )
        time.sleep(0.1)
        
        # 2. Add dummy system metrics
        SystemMetricsModel.log_metrics(12.5, 45.8, 10.2, 5120, 2048)
        SystemMetricsModel.log_metrics(18.9, 46.1, 10.2, 10240, 4096)
        
        # 3. Add dummy traffic metrics
        TrafficMetricsModel.log_metrics(100, 12, 1.25)
        TrafficMetricsModel.log_metrics(150, 15, 2.10)
        
        # 4. Add a mock alert
        AlertModel.trigger_alert("RED", "Critical request rate exceeded thresholds", "192.168.1.99")
        
        # 5. Add a mock mitigation block action
        MitigationActionModel.log_action("BLOCK_IP", "192.168.1.99", 60)
        
        # 6. Stop the mock experiment
        ExperimentModel.stop_experiment(exp_id)
        
        # 7. Compile report PDF
        pdf_path = generate_pdf_report(exp_id)
        self.assertIsNotNone(pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        
        # 8. Assert PDF layout format (Verify PDF magic bytes header)
        with open(pdf_path, 'rb') as f:
            header = f.read(4)
            self.assertEqual(header, b'%PDF')

        # Cleanup local test PDF file
        try:
            os.remove(pdf_path)
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main()
