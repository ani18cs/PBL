import time
import threading
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_second_limit=10):
        self.lock = threading.Lock()
        self.limit = requests_per_second_limit
        # Mapping IP -> list of timestamps within current window
        self.request_windows = defaultdict(list)

    def is_rate_limited(self, ip):
        """Checks if the client IP is exceeding rate limits (sliding window 1s)."""
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return False
        now = time.time()
        with self.lock:
            # Filter request timestamps outside of 1-second window
            self.request_windows[ip] = [t for t in self.request_windows[ip] if now - t < 1.0]
            
            if len(self.request_windows[ip]) >= self.limit:
                return True
                
            self.request_windows[ip].append(now)
            return False

    def update_limit(self, new_limit):
        """Updates the per-IP limit threshold."""
        with self.lock:
            self.limit = new_limit
            print(f"[RateLimiter] Limit threshold updated to {new_limit} requests/sec")
