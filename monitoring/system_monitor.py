import psutil
import time

class SystemMonitor:
    def __init__(self):
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()

    def sample_metrics(self):
        """Returns CPU usage, Memory usage, Disk usage, Network In/Out rates."""
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        
        # Disk usage of the current partition
        try:
            disk = psutil.disk_usage('/').percent
        except Exception:
            disk = 0.0
            
        # Calculate network throughput rates (Bytes/sec)
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        
        time_delta = current_time - self.last_time
        if time_delta <= 0:
            time_delta = 0.01  # prevent zero division
            
        bytes_recv_diff = current_net_io.bytes_recv - self.last_net_io.bytes_recv
        bytes_sent_diff = current_net_io.bytes_sent - self.last_net_io.bytes_sent
        
        net_in = bytes_recv_diff / time_delta
        net_out = bytes_sent_diff / time_delta
        
        # Update references
        self.last_net_io = current_net_io
        self.last_time = current_time
        
        return {
            "cpu": cpu,
            "memory": mem,
            "disk": disk,
            "network_in": net_in,
            "network_out": net_out
        }
