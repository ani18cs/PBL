import threading
import time
from flask_socketio import SocketIO
from dashboard import state

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on("connect", namespace="/stats")
def on_stats_connect():
    pass

@socketio.on("disconnect", namespace="/stats")
def on_stats_disconnect():
    pass

def start_socketio_emitter():
    """Starts the background thread that continuously queries stats and broadcasts them."""
    def emit_log(msg):
        socketio.emit("security_log", {"message": msg}, namespace="/stats")
    state.log_callback = emit_log
    
    thread = threading.Thread(
        target=_websocket_emitter_loop, daemon=True, name="WebSocketEmitter"
    )
    thread.start()
    print("[WebSocket] Background SocketIO emitter thread active.")

def _websocket_emitter_loop():
    while True:
        time.sleep(1.0)
        
        # Verify references exist before sampling
        if not state.server_instance or not state.metrics_collector or not state.detector_instance:
            continue
            
        try:
            # 1. Fetch current 1-second interval stats from Target Server
            req_count = state.server_instance.last_req_count
            active_count = state.server_instance.last_active_count
            avg_lat = state.server_instance.last_avg_lat
            
            # Fetch last active client IP history in the window
            histories = state.server_instance.conn_manager.get_client_histories()
            ip_list = []
            for h in histories:
                ip_list.extend([h["ip"]] * h["request_count"])
                
            # 2. Run traffic slice through detection engine and get severity
            current_severity = state.detector_instance.process_traffic_slice(
                req_count, active_count, ip_list
            )
            
            # Apply automatic/manual mitigation decision hooks
            if state.mitigation_controller:
                for ip in set(ip_list):
                    # Check rate limits first
                    if state.mitigation_controller.rate_limiter.is_rate_limited(ip):
                        if state.mitigation_controller.mode == "automatic":
                            state.mitigation_controller.blacklist_manager.block_ip(ip, duration_seconds=30)
                            
                    # Check connection limits
                    # Note: server thread handles connection registering, but check here as well if needed.
                    pass
                    
            # 3. Pull latest psutil system metrics
            sys_metrics = state.metrics_collector.monitor.sample_metrics()
            
            # 4. Pull active blocklists
            blocked_ips = []
            mitigation_mode = "automatic"
            if state.mitigation_controller:
                blocked_ips = state.mitigation_controller.blacklist_manager.get_blocked_ips()
                mitigation_mode = state.mitigation_controller.mode
                
            # Compile statistics update dictionary
            payload = {
                "timestamp": time.strftime("%H:%M:%S"),
                "cpu": sys_metrics["cpu"],
                "memory": sys_metrics["memory"],
                "disk": sys_metrics["disk"],
                "network_in": sys_metrics["network_in"],
                "network_out": sys_metrics["network_out"],
                "requests_per_second": req_count,
                "active_connections": active_count,
                "average_latency": avg_lat,
                "severity": current_severity,
                "blocked_ips": blocked_ips,
                "mode": mitigation_mode,
                "active_experiment": state.active_experiment_name
            }
            
            # Broadcast statistics update via namespace channel
            socketio.emit("metrics_update", payload, namespace="/stats")
            
        except Exception:
            pass
