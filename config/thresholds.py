# DDoS Detection Threshold configurations

# Packets Per Second (PPS) / Requests Per Second thresholds
PPS_SUSPICIOUS_THRESHOLD = 50
PPS_ATTACK_THRESHOLD = 150

# Active Connection thresholds
CONN_SUSPICIOUS_THRESHOLD = 20
CONN_ATTACK_THRESHOLD = 50

# Burst detection settings (multiplier of moving average)
BURST_WINDOW_SIZE = 10  # Seconds
BURST_THRESHOLD_MULTIPLIER = 2.5

# Shannon Entropy thresholds (low entropy indicates single source IP / Protocol focus)
ENTROPY_IP_THRESHOLD = 1.2
ENTROPY_PROTO_THRESHOLD = 0.5
