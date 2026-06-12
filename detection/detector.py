import time
from collections import Counter
from detection.rate_analyzer import RateAnalyzer
from detection.burst_detector import BurstDetector
from detection.anomaly_detector import AnomalyDetector
from database.models import AlertModel

class DDoSDetector:
    def __init__(self):
        self.rate_analyzer = RateAnalyzer()
        self.burst_detector = BurstDetector()
        self.anomaly_detector = AnomalyDetector()
        self.current_severity = "GREEN"

    def process_traffic_slice(self, requests_sec, active_connections, ip_list):
        """Processes a 1-second slice of traffic metrics and generates database alerts."""
        severities = []
        alerts_raised = []
        
        # 1. Analyze rate thresholds
        rate_sev, rate_desc = self.rate_analyzer.analyze(requests_sec)
        severities.append(rate_sev)
        if rate_sev != "GREEN":
            alerts_raised.append((rate_sev, rate_desc))
            
        # 2. Analyze sudden burst limits
        burst_sev, burst_desc = self.burst_detector.analyze(requests_sec)
        severities.append(burst_sev)
        if burst_sev != "GREEN":
            alerts_raised.append((burst_sev, burst_desc))
            
        # 3. Analyze source IP entropy
        entropy_sev, entropy_desc, _ = self.anomaly_detector.analyze(ip_list)
        severities.append(entropy_sev)
        if entropy_sev != "GREEN":
            alerts_raised.append((entropy_sev, entropy_desc))
            
        # 4. Resolve overall active alert severity
        priority = {"GREEN": 0, "YELLOW": 1, "ORANGE": 2, "RED": 3}
        max_severity = "GREEN"
        for sev in severities:
            if priority[sev] > priority[max_severity]:
                max_severity = sev
                
        self.current_severity = max_severity
        
        # 5. Log triggered alerts to database
        for sev, desc in alerts_raised:
            dominant_ip = None
            if len(ip_list) > 0:
                counts = Counter(ip_list)
                most_common = counts.most_common(1)[0]
                # If a single IP makes up more than 50% of the traffic slice
                if most_common[1] / len(ip_list) >= 0.5:
                    dominant_ip = most_common[0]
                    
            AlertModel.trigger_alert(sev, desc, dominant_ip)
            msg = f"[{sev} Alert] {desc} (IP: {dominant_ip if dominant_ip else 'N/A'})"
            print(f"[DDoSDetector] {msg}")
            try:
                from dashboard import state
                state.add_log("DDoSDetector", msg)
            except Exception:
                pass
            
        return self.current_severity
