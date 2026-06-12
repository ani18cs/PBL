import threading
import time
from simulator.traffic_profiles import TRAFFIC_PROFILES
from simulator.traffic_generator import TrafficGenerator
from database.models import ExperimentModel

class ExperimentRunner:
    def __init__(self, target_host="127.0.0.1", target_port=8080):
        self.generator = TrafficGenerator(target_host, target_port)
        self.active_experiment_id = None
        self.timer_thread = None

    def run_experiment(self, name, profile_name, duration_seconds):
        """Starts an experiment profile in the background, logging to database."""
        if self.active_experiment_id is not None:
            print("[ExperimentRunner] An experiment is already running.")
            return False
            
        if profile_name not in TRAFFIC_PROFILES:
            print(f"[ExperimentRunner] Profile '{profile_name}' not found.")
            return False
            
        profile_config = TRAFFIC_PROFILES[profile_name]
        
        # 1. Log start in DB
        config_payload = {
            "profile": profile_name,
            "duration": duration_seconds,
            "clients": profile_config["clients"],
            "request_interval": profile_config["request_interval"],
            "concurrency": profile_config["concurrency"]
        }
        self.active_experiment_id = ExperimentModel.start_experiment(name, config_payload)
        
        # 2. Trigger Traffic Generator
        self.generator.start_profile(profile_config)
        
        # 3. Schedule auto-stop timer
        self.timer_thread = threading.Thread(
            target=self._duration_timer,
            args=(duration_seconds,),
            daemon=True,
            name="ExperimentTimer"
        )
        self.timer_thread.start()
        
        print(f"[ExperimentRunner] Running experiment '{name}' (ID: {self.active_experiment_id}) for {duration_seconds}s...")
        try:
            from dashboard import state
            state.add_log("Simulator", f"Started experiment '{name}' ({profile_name.upper()} profile, {duration_seconds}s)")
        except Exception:
            pass
        return True

    def stop_active_experiment(self):
        """Halts the active experiment and updates end_time status in SQLite."""
        if self.active_experiment_id is None:
            return False
            
        # Stop traffic
        self.generator.stop()
        
        # Log stop in DB
        ExperimentModel.stop_experiment(self.active_experiment_id)
        print(f"[ExperimentRunner] Experiment ID {self.active_experiment_id} stopped.")
        try:
            from dashboard import state
            state.add_log("Simulator", f"Stopped active experiment ID {self.active_experiment_id}")
        except Exception:
            pass
        
        self.active_experiment_id = None
        
        # Reset the dashboard active experiment name to release the UI run lock
        try:
            from dashboard import state as db_state
            db_state.active_experiment_name = None
        except ImportError:
            pass
            
        return True

    def _duration_timer(self, duration):
        """Timer callback loop that terminates generator traffic once expired."""
        time.sleep(duration)
        if self.active_experiment_id is not None:
            self.stop_active_experiment()
