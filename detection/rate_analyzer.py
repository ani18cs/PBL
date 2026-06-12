from config.thresholds import PPS_SUSPICIOUS_THRESHOLD, PPS_ATTACK_THRESHOLD

class RateAnalyzer:
    def analyze(self, requests_sec):
        """Analyzes requests per second, returns alert level ('GREEN', 'YELLOW', 'RED') and description."""
        if requests_sec >= PPS_ATTACK_THRESHOLD:
            return "RED", f"Critical request rate detected: {requests_sec} requests/sec"
        elif requests_sec >= PPS_SUSPICIOUS_THRESHOLD:
            return "YELLOW", f"Suspicious request rate detected: {requests_sec} requests/sec"
        return "GREEN", "Normal request rate"
