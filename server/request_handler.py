import time
import socket

def handle_client_socket(client_sock, client_addr, conn_manager, mitigation_controller=None):
    """Processes connection commands, measures latency, and handles socket cleanup."""
    conn_manager.register_conn(client_sock, client_addr)
    ip = client_addr[0]
    
    try:
        client_sock.settimeout(5.0)  # 5-second idle timeout
        last_ip = ip
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
                
            request_str = ""
            try:
                request_str = data.decode("utf-8", errors="ignore")
            except Exception:
                pass
                
            current_ip = ip
            if "Host:" in request_str:
                for line in request_str.split("\r\n"):
                    if line.strip().startswith("Host:"):
                        host_val = line.split(":", 1)[1].strip()
                        if ":" in host_val:
                            host_val = host_val.split(":", 1)[0]
                        if host_val not in ["localhost", "127.0.0.1"]:
                            current_ip = host_val
                        break
            
            last_ip = current_ip

            # Mitigation limit rate checking
            if mitigation_controller:
                if not mitigation_controller.handle_request(current_ip):
                    break
                
            start_time = time.time()
            
            # Simulate a brief processing latency (2 milliseconds)
            time.sleep(0.002)
            
            latency = (time.time() - start_time) * 1000.0  # in milliseconds
            conn_manager.register_request(current_ip, latency)
            
            # Respond to client
            client_sock.sendall(b"ACK\n")
            
    except (socket.timeout, socket.error):
        pass
    except Exception:
        pass
    finally:
        try:
            client_sock.close()
        except Exception:
            pass
        conn_manager.unregister_conn(client_sock)
        if mitigation_controller:
            mitigation_controller.handle_connection_close(last_ip)
