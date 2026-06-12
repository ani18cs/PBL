# dashboard/state.py

# Shared reference variables between dashboard routes, socket events, and background processes
server_instance = None
experiment_runner = None
metrics_collector = None
detector_instance = None
mitigation_controller = None
active_experiment_name = None

log_buffer = []
log_callback = None

def add_log(category, message):
    import time
    timestamp = time.strftime("%H:%M:%S")
    formatted = f"[{timestamp}] [{category}] {message}"
    log_buffer.append(formatted)
    if len(log_buffer) > 2000:
        log_buffer.pop(0)
    if log_callback:
        try:
            log_callback(formatted)
        except Exception:
            pass
