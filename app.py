from flask import Flask
from database.database import init_db
from server.target_server import TargetServer
from simulator.experiment_runner import ExperimentRunner
from monitoring.metrics_collector import MetricsCollector
from detection.detector import DDoSDetector
from mitigation.mitigation_controller import MitigationController
from dashboard.routes import bp as dashboard_bp
from dashboard.websocket import socketio, start_socketio_emitter
from dashboard import state

# 1. Initialize components
init_db()

server = TargetServer(host="127.0.0.1", port=8080)
mitigation = MitigationController()

# Bind mitigation checker to target server socket accept loop
server.mitigation_controller = mitigation

runner = ExperimentRunner(target_host="127.0.0.1", target_port=8080)
collector = MetricsCollector(interval=1.0)
detector = DDoSDetector()

# 2. Bind global shared registry references
state.server_instance = server
state.experiment_runner = runner
state.metrics_collector = collector
state.detector_instance = detector
state.mitigation_controller = mitigation

import os as _os
_TEMPLATE_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "dashboard", "templates")

# 3. Create Flask app
app = Flask(__name__, template_folder=_TEMPLATE_DIR)
app.config["SECRET_KEY"] = "cyber_security_educational_platform"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True
app.register_blueprint(dashboard_bp)

socketio.init_app(app)

if __name__ == "__main__":
    try:
        # Start core background socket listener loop
        server.start()
        
        # Start resource collector (psutil) logging loop
        collector.start()
        
        # Launch websocket stats loop
        start_socketio_emitter()
        
        print("="*60)
        print("   DEFCON-D DDOS SECURITY EDUCATIONAL PLATFORM RUNNING")
        print("="*60)
        
        # Start Flask SocketIO server on port 5000 with Werkzeug fallback allowance
        socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        pass
    finally:
        print("[App] Shutting down background tasks...")
        server.stop()
        collector.stop()
