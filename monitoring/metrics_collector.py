import threading
import time
from monitoring.system_monitor import SystemMonitor
from database.models import SystemMetricsModel

class MetricsCollector:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.monitor = SystemMonitor()
        self.running = False
        self.thread = None

    def start(self):
        """Starts the background loop to sample and log system metrics."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(
            target=self._collect_loop, daemon=True, name="MetricsCollectorLoop"
        )
        self.thread.start()
        print("[MetricsCollector] System metrics collector daemon thread started.")

    def stop(self):
        """Stops the collector thread."""
        self.running = False
        print("[MetricsCollector] System metrics collector stopped.")

    def _collect_loop(self):
        while self.running:
            start_time = time.time()
            
            try:
                metrics = self.monitor.sample_metrics()
                SystemMetricsModel.log_metrics(
                    metrics["cpu"],
                    metrics["memory"],
                    metrics["disk"],
                    metrics["network_in"],
                    metrics["network_out"]
                )
            except Exception:
                pass
                
            # Align execution times to exact interval offsets
            elapsed = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)
