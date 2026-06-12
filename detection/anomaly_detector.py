import math
from collections import Counter
from config.thresholds import ENTROPY_IP_THRESHOLD

class AnomalyDetector:
    @staticmethod
    def calculate_entropy(ip_list):
        """Calculates Shannon entropy on list of source IPs. Returns float bits value."""
        if not ip_list:
            return 0.0
            
        counts = Counter(ip_list)
        total = len(ip_list)
        
        entropy = 0.0
        for ip, count in counts.items():
            prob = count / total
            entropy -= prob * math.log2(prob)
            
        return entropy

    def analyze(self, ip_list):
        """Analyzes entropy levels. Lower entropy implies high concentration (attack)."""
        if len(ip_list) < 10:
            return "GREEN", "Awaiting baseline traffic size", 0.0
            
        entropy = self.calculate_entropy(ip_list)
        
        if entropy < ENTROPY_IP_THRESHOLD:
            return "RED", f"Low IP distribution entropy: {entropy:.2f} bits (Targeted flood indicator)", entropy
            
        return "GREEN", f"Normal IP distribution entropy: {entropy:.2f} bits", entropy
