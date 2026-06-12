import threading
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.active_connections = {}  # socket -> client_address
        self.client_stats = defaultdict(lambda: {
            "request_count": 0,
            "connection_count": 0,
            "total_latency": 0.0,
            "last_active": 0.0
        })
        self.total_requests = 0
        self.latency_samples = []

    def register_conn(self, client_sock, client_addr):
        """Registers an active connection socket."""
        with self.lock:
            self.active_connections[client_sock] = client_addr
            ip = client_addr[0]
            self.client_stats[ip]["connection_count"] += 1
            self.client_stats[ip]["last_active"] = client_addr[1]

    def unregister_conn(self, client_sock):
        """Unregisters a connection socket on close."""
        with self.lock:
            if client_sock in self.active_connections:
                del self.active_connections[client_sock]

    def register_request(self, ip, latency):
        """Tracks latency and increments total request metrics."""
        with self.lock:
            self.total_requests += 1
            self.client_stats[ip]["request_count"] += 1
            self.client_stats[ip]["total_latency"] += latency
            self.latency_samples.append(latency)

    def get_active_count(self):
        """Returns current active socket connection count."""
        with self.lock:
            return len(self.active_connections)

    def pop_metrics(self):
        """Extracts stats window metrics and clears latency samples."""
        with self.lock:
            req_count = self.total_requests
            self.total_requests = 0
            
            active_count = len(self.active_connections)
            
            if self.latency_samples:
                avg_lat = sum(self.latency_samples) / len(self.latency_samples)
                self.latency_samples.clear()
            else:
                avg_lat = 0.0
                
            return req_count, active_count, avg_lat

    def get_client_histories(self):
        """Returns list snapshot of per-IP request statistics."""
        with self.lock:
            histories = []
            for ip, stats in self.client_stats.items():
                avg_lat = 0.0
                if stats["request_count"] > 0:
                    avg_lat = stats["total_latency"] / stats["request_count"]
                histories.append({
                    "ip": ip,
                    "request_count": stats["request_count"],
                    "connection_count": stats["connection_count"],
                    "average_latency": avg_lat
                })
            return histories
