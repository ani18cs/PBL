TRAFFIC_PROFILES = {
    "normal": {
        "clients": 10,
        "request_interval": 0.5,  # delay between requests in seconds
        "concurrency": 2,
        "description": "Legitimate baseline user traffic pattern"
    },
    "medium": {
        "clients": 30,
        "request_interval": 0.2,
        "concurrency": 5,
        "description": "Moderately elevated traffic load"
    },
    "heavy": {
        "clients": 80,
        "request_interval": 0.05,
        "concurrency": 15,
        "description": "Simulated distributed flood loading"
    },
    "stress": {
        "clients": 150,
        "request_interval": 0.01,
        "concurrency": 30,
        "description": "High-intensity stress test payload"
    }
}
