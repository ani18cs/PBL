import threading
from collections import defaultdict

class ConnectionLimiter:
    def __init__(self, max_concurrent_connections=5):
        self.lock = threading.Lock()
        self.limit = max_concurrent_connections
        # Mapping IP -> active connection count
        self.active_counts = defaultdict(int)

    def register_connection(self, ip):
        """Increments active connections count for IP. Returns False if limit is exceeded."""
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return True
        with self.lock:
            if self.active_counts[ip] >= self.limit:
                return False
            self.active_counts[ip] += 1
            return True

    def unregister_connection(self, ip):
        """Decrements active connection counts."""
        with self.lock:
            if ip in self.active_counts and self.active_counts[ip] > 0:
                self.active_counts[ip] -= 1

    def update_limit(self, new_limit):
        """Updates connection concurrency limit."""
        with self.lock:
            self.limit = new_limit
            print(f"[ConnectionLimiter] Concurrent connection limit updated to {new_limit}")
