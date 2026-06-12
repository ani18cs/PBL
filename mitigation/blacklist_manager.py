import threading
import time
from database.models import MitigationActionModel

class BlacklistManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.blacklist = {}  # ip -> unblock_timestamp

    def block_ip(self, ip, duration_seconds=60):
        """Temporarily blocks an IP address."""
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return
        with self.lock:
            unblock_at = time.time() + duration_seconds
            self.blacklist[ip] = unblock_at
            MitigationActionModel.log_action("BLOCK_IP", ip, duration_seconds)
            print(f"[BlacklistManager] Blocked IP {ip} for {duration_seconds}s")
            try:
                from dashboard import state
                state.add_log("Firewall", f"Blocked IP {ip} for {duration_seconds}s")
            except Exception:
                pass

    def unblock_ip(self, ip):
        """Removes an IP block manually."""
        with self.lock:
            if ip in self.blacklist:
                del self.blacklist[ip]
                MitigationActionModel.log_action("UNBLOCK_IP", ip)
                print(f"[BlacklistManager] Unblocked IP {ip}")
                try:
                    from dashboard import state
                    state.add_log("Firewall", f"Manually unblocked IP {ip}")
                except Exception:
                    pass

    def is_blocked(self, ip):
        """Checks if an IP is blocked, automatically lifting expired blocks."""
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return False
        now = time.time()
        with self.lock:
            if ip in self.blacklist:
                if now < self.blacklist[ip]:
                    return True
                else:
                    # Block expired, lift automatically
                    del self.blacklist[ip]
                    # Log lifter in a separate quick thread to avoid blocking check
                    threading.Thread(
                        target=MitigationActionModel.log_action,
                        args=("LIFT_LIMIT", ip),
                        daemon=True
                    ).start()
                    print(f"[BlacklistManager] Expired block lifted for IP {ip}")
                    try:
                        from dashboard import state
                        state.add_log("Firewall", f"Expired block lifted for IP {ip}")
                    except Exception:
                        pass
            return False

    def get_blocked_ips(self):
        """Returns list of currently blocked IPs and remaining seconds."""
        now = time.time()
        with self.lock:
            # Lift expired items
            expired = [ip for ip, expiry in self.blacklist.items() if now >= expiry]
            for ip in expired:
                del self.blacklist[ip]
                
            return [
                {"ip": ip, "remaining": max(0, int(expiry - now))}
                for ip, expiry in self.blacklist.items()
            ]
