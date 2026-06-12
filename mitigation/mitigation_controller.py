from mitigation.blacklist_manager import BlacklistManager
from mitigation.rate_limiter import RateLimiter
from mitigation.connection_limiter import ConnectionLimiter

class MitigationController:
    def __init__(self):
        self.blacklist_manager = BlacklistManager()
        self.rate_limiter = RateLimiter(requests_per_second_limit=15)
        self.connection_limiter = ConnectionLimiter(max_concurrent_connections=8)
        self.mode = "automatic"  # manual, automatic, hybrid

    def set_mode(self, mode):
        """Sets the active mitigation mode: manual, automatic, hybrid."""
        if mode in ["manual", "automatic", "hybrid"]:
            self.mode = mode
            print(f"[MitigationController] Mode set to: {mode.upper()}")
            return True
        return False

    def handle_incoming_connection(self, ip):
        """Checks if connection should be allowed. Returns True if allowed, False if blocked."""
        # 1. Apply firewall blocklist rules
        if self.blacklist_manager.is_blocked(ip):
            return False

        # 2. Check connection concurrency limits
        if not self.connection_limiter.register_connection(ip):
            if self.mode == "automatic":
                # Automatically block IP for 60 seconds
                self.blacklist_manager.block_ip(ip, duration_seconds=60)
            return False
            
        return True

    def handle_request(self, ip):
        """Checks if request is allowed. Returns True if allowed, False if rate limited."""
        # 1. Apply firewall blocklist rules
        if self.blacklist_manager.is_blocked(ip):
            return False

        # 2. Check per-IP request frequency limits
        if self.rate_limiter.is_rate_limited(ip):
            if self.mode == "automatic":
                # Automatically block offender IP for 30 seconds
                self.blacklist_manager.block_ip(ip, duration_seconds=30)
            return False

        return True

    def handle_connection_close(self, ip):
        """Releases the concurrency connection reservation on close."""
        self.connection_limiter.unregister_connection(ip)
