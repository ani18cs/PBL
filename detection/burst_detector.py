from collections import deque
from config.thresholds import BURST_WINDOW_SIZE, BURST_THRESHOLD_MULTIPLIER

class BurstDetector:
    def __init__(self):
        self.history = deque(maxlen=BURST_WINDOW_SIZE)

    def analyze(self, current_pps):
        """Compares current traffic against moving average. Triggers alert on sudden spikes."""
        if len(self.history) < 3:
            self.history.append(current_pps)
            return "GREEN", "Awaiting sufficient history metrics for burst calculation"
            
        avg = sum(self.history) / len(self.history)
        self.history.append(current_pps)
        
        if avg > 1.0 and current_pps >= avg * BURST_THRESHOLD_MULTIPLIER:
            return "ORANGE", f"Sudden traffic burst spike: {current_pps} pps (Moving Average: {avg:.1f} pps)"
            
        return "GREEN", "No traffic burst detected"
