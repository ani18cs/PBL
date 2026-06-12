import socket
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

def _log(msg):
    """Best-effort log to dashboard state without hard import dependency."""
    try:
        from dashboard import state
        state.add_log("TrafficGen", msg)
    except Exception:
        pass

class TrafficGenerator:
    def __init__(self, target_host="127.0.0.1", target_port=8080):
        self.target_host = target_host
        self.target_port = target_port
        self.running = False
        self.executor = None
        self.futures = []

    def start_profile(self, profile_config):
        """Starts client request loops matching the profile options."""
        if self.running:
            return
        self.running = True
        
        clients = profile_config.get("clients", 10)
        interval = profile_config.get("request_interval", 0.5)
        concurrency = profile_config.get("concurrency", 2)
        
        self.executor = ThreadPoolExecutor(max_workers=concurrency)
        
        for i in range(clients):
            client_ip = f"192.168.1.{100 + i}"
            future = self.executor.submit(self._client_loop, client_ip, interval)
            self.futures.append(future)
            
        print(f"[TrafficGenerator] Started {clients} clients with concurrency {concurrency}")
        _log(f"Spawned {clients} virtual clients · interval={interval}s · concurrency={concurrency}")

    def stop(self):
        """Halts client loops and shuts down executor."""
        self.running = False
        if self.executor:
            self.executor.shutdown(wait=False)
        self.futures.clear()
        print("[TrafficGenerator] Stopped generator traffic loops.")
        _log("Traffic generator stopped — all client loops halted.")

    def _client_loop(self, client_ip, interval):
        """Repeatedly establishes TCP sockets and sends messages to simulate loading."""
        current_ip = client_ip
        while self.running:
            try:
                # Target host validation check (educational security guardrail)
                is_internal = (
                    self.target_host in ["127.0.0.1", "localhost"] or
                    self.target_host.startswith("10.") or
                    self.target_host.startswith("192.168.") or
                    self.target_host.startswith("172.16.") or
                    self.target_host.startswith("172.17.") or
                    self.target_host.startswith("172.18.") or
                    self.target_host.startswith("172.19.") or
                    self.target_host.startswith("172.20.") or
                    self.target_host.startswith("172.21.") or
                    self.target_host.startswith("172.22.") or
                    self.target_host.startswith("172.23.") or
                    self.target_host.startswith("172.24.") or
                    self.target_host.startswith("172.25.") or
                    self.target_host.startswith("172.26.") or
                    self.target_host.startswith("172.27.") or
                    self.target_host.startswith("172.28.") or
                    self.target_host.startswith("172.29.") or
                    self.target_host.startswith("172.30.") or
                    self.target_host.startswith("172.31.")
                )
                if not is_internal:
                    print("[TrafficGenerator] Guardrail Alert: Target server is external. ACCIDENTAL ATTACK BLOCKED.")
                    _log(f"GUARDRAIL: External target blocked for {current_ip} — only localhost/private IPs allowed.")
                    break

                # Connect client socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.target_host, self.target_port))
                
                # Apply randomized jitter delay
                actual_delay = interval * random.uniform(0.8, 1.2)
                
                # Send standard request payload
                payload = f"GET / HTTP/1.1\r\nHost: {current_ip}\r\n\r\n"
                sock.sendall(payload.encode())
                
                response = b""
                try:
                    response = sock.recv(1024)  # Read server response (ACK)
                except Exception:
                    pass
                
                if not response:
                    status = "---"
                    _log(f"REQ  {current_ip} → {self.target_host}:{self.target_port}  [{status}]  delay={actual_delay:.3f}s")
                    # Rotate to a new IP since this one was blocked
                    old_ip = current_ip
                    current_ip = f"192.168.1.{random.randint(100, 250)}"
                    while current_ip == old_ip:
                        current_ip = f"192.168.1.{random.randint(100, 250)}"
                else:
                    status = "200 OK" if b"200" in response else ("429" if b"429" in response else "---")
                    _log(f"REQ  {current_ip} → {self.target_host}:{self.target_port}  [{status}]  delay={actual_delay:.3f}s")
                    
                sock.close()
                time.sleep(actual_delay)
                
            except Exception as e:
                _log(f"ERR  {current_ip} → connection failed: {e}")
                # Rotate IP on connection failure
                current_ip = f"192.168.1.{random.randint(100, 250)}"
                time.sleep(0.5)
