import socket
import threading
import time
from server.connection_manager import ConnectionManager
from server.request_handler import handle_client_socket
from database.models import TrafficMetricsModel, ConnectionHistoryModel

class TargetServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.conn_manager = ConnectionManager()
        self.mitigation_controller = None
        self.server_socket = None
        self.running = False
        self.listener_thread = None
        self.monitor_thread = None
        self.last_req_count = 0
        self.last_active_count = 0
        self.last_avg_lat = 0.0

    def start(self):
        """Starts the server listener loop and monitor logger thread."""
        if self.running:
            return
            
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(128)
        
        self.listener_thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="ServerListener"
        )
        self.listener_thread.start()
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_log_loop, daemon=True, name="ServerMonitorLogger"
        )
        self.monitor_thread.start()
        
        print(f"[TargetServer] Server listening on {self.host}:{self.port}")

    def stop(self):
        """Gracefully shuts down sockets and background logging loops."""
        self.running = False
        if self.server_socket:
            try:
                # Force close socket to break the accept() blocking state
                self.server_socket.close()
            except Exception:
                pass
        print("[TargetServer] Server stopped.")

    def _listen_loop(self):
        while self.running:
            try:
                client_sock, client_addr = self.server_socket.accept()
                ip = client_addr[0]
                
                # Mitigation check: Drop if blacklisted or concurrent limit reached
                if self.mitigation_controller:
                    if not self.mitigation_controller.handle_incoming_connection(ip):
                        try:
                            client_sock.close()
                        except Exception:
                            pass
                        continue
                        
                t = threading.Thread(
                    target=handle_client_socket,
                    args=(client_sock, client_addr, self.conn_manager, self.mitigation_controller),
                    daemon=True,
                    name=f"ClientHandler-{client_addr[0]}:{client_addr[1]}"
                )
                t.start()
            except Exception:
                # Catch closed socket exceptions on stop
                break

    def _monitor_log_loop(self):
        """Saves traffic and connection history metrics to SQLite database every 1 second."""
        while self.running:
            time.sleep(1.0)
            if not self.running:
                break
                
            # Pop and record window metrics
            req_count, active_count, avg_lat = self.conn_manager.pop_metrics()
            self.last_req_count = req_count
            self.last_active_count = active_count
            self.last_avg_lat = avg_lat
            
            try:
                # Log metrics to DB
                TrafficMetricsModel.log_metrics(req_count, active_count, avg_lat)
                
                # Snapshot and save current histories
                histories = self.conn_manager.get_client_histories()
                for h in histories:
                    ConnectionHistoryModel.log_history(
                        h["ip"],
                        h["request_count"],
                        h["connection_count"],
                        h["average_latency"]
                    )
                
                # Log summary to console if there's active traffic
                if req_count > 0:
                    try:
                        from dashboard import state
                        state.add_log("TargetServer", f"Traffic: {req_count} pps | Active Conns: {active_count} | Avg Latency: {avg_lat:.2f}ms")
                    except Exception:
                        pass
            except Exception as e:
                # Fail silently or log
                pass

if __name__ == "__main__":
    from database.database import init_db
    init_db()
    server = TargetServer()
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
