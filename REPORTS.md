# 🛡️ DEFCON-D DDoS Platform: Comprehensive Technical Report (A-Z Details)

This report provides a detailed documentation of the **DEFCON-D DDoS Simulation, Detection, and Mitigation Platform** architecture, backend systems, simulator operations, and mitigation strategies.

---

## 1. Executive Summary & Architecture Overview

DEFCON-D is an educational cybersecurity platform designed to demonstrate target server performance drops under load, anomaly-based DDoS detection metrics, and mitigation rules deployment in a safe, private environment.

The system is structured into five core layers:
1. **Traffic Simulator**: Generates traffic profiles to model baseline user patterns and various scale DDoS attacks.
2. **Target TCP Server**: A custom multithreaded socket server that handles HTTP requests and tracks connection metadata.
3. **Detection Engine**: Evaluates request rate thresholds, moving average burst indicators, and Shannon entropy distributions on source IPs.
4. **Mitigation Engine**: Enforces active blocklists, per-IP connection limits, and sliding window request rate limiting.
5. **Telemetry & Dashboard**: Logs performance metrics to an SQLite database, streams logs in real time via Socket.IO, and supports PDF report downloads.

```
         Traffic Simulator (Normal / Stress load profiles)
                             |
                             V (TCP client socket streams)
                       Target Server (connection registry, latency counters)
                             |
                  +----------+----------+
                  |                     |
                  V                     V
           Monitoring Layer      DDoS Detection Engine (Rate, Burst, Entropy)
                  |                     |
                  +----------+----------+
                             |
                             V
                     Mitigation Engine (Blacklist blocks, sliding window rate limits)
                             |
                  +----------+----------+
                  |                     |
                  V                     V
             SQLite Database     SocketIO Dashboard / PDF Reports
```

---

## 2. Backend Systems Details

### A. Target TCP Server (`server/`)
* **`server/target_server.py`**: Initiates a TCP server on port `8080`. It runs a `listener_thread` that waits for socket connections (`socket.accept()`) and handles client connections in separate threads (`ClientHandler-*`). It also spawns a `monitor_thread` that aggregates and logs performance data every second.
* **`server/connection_manager.py`**: Thread-safe tracker recording active connection counts, aggregate request counts, latency windows, and individual client IP history.
* **`server/request_handler.py`**: Reads client HTTP headers, measures execution delay, matches incoming IPs against mitigation rules, and replies with appropriate response payloads (`200 OK` or `429 Too Many Requests` / blocks).

### B. Database Schema & Models (`database/`)
All platform telemetry is recorded in `database/ddos_platform.db` using a SQLite relational database:
* **`experiments`**: Logs simulator settings (run metadata, active profile, duration).
* **`system_metrics`**: Logs CPU usage, Memory utilization, Disk usage, and Network I/O bytes.
* **`traffic_metrics`**: Records requests per second (PPS), active connection counts, and average request latency.
* **`connection_history`**: Tracks request distribution, concurrency, and response latency grouped by client source IP.
* **`alerts`**: Stores triggered security alerts, details, and dominant offender source IPs.
* **`mitigation_actions`**: Logs firewall blacklist updates, rate-limiting actions, and unblock execution details.

---

## 3. Traffic Simulation & Profiles (`simulator/`)

The simulator generates multi-client socket loads targeted at the server.

### A. Traffic Profiles (`simulator/traffic_profiles.py`)
Four profiles represent different scales of user activity:
1. **`normal`**: 10 clients, 0.5s intervals, concurrency of 2. Represents legitimate baseline user behavior.
2. **`medium`**: 30 clients, 0.2s intervals, concurrency of 5. Simulates moderately elevated traffic.
3. **`heavy`**: 80 clients, 0.05s intervals, concurrency of 15. Simulates a distributed HTTP flood.
4. **`stress`**: 150 clients, 0.01s intervals, concurrency of 30. Simulates high-intensity stress testing.

### B. Traffic Generator (`simulator/traffic_generator.py`)
Spawns virtual client threads using a `ThreadPoolExecutor`. Each client acts as a distinct source IP (`192.168.1.100` to `192.168.1.250`).
* **Jitter & Network Delay**: Requests are randomized with a jitter multiplier of `0.8 - 1.2` against the profile interval.
* **Safety Guardrails**: A built-in guardrail validates the target host. If the target matches an external domain or public IP, the generator blocks execution immediately, preventing accidental attacks on public infrastructure.

---

## 4. DDoS Detection Engine (`detection/`)

The platform utilizes three complementary detection strategies to classify threat severity (`GREEN`, `YELLOW`, `ORANGE`, `RED`):

### A. Rate Analyzer (`detection/rate_analyzer.py`)
Checks absolute requests-per-second thresholds:
* **Suspicious Level**: > 50 Requests/sec (`PPS_SUSPICIOUS_THRESHOLD`). Triggers `YELLOW`.
* **Attack Level**: > 150 Requests/sec (`PPS_ATTACK_THRESHOLD`). Triggers `RED`.

### B. Burst Detector (`detection/burst_detector.py`)
Monitors sudden spikes by comparing current traffic to a moving average over a sliding 10-second window.
* **Burst Trigger**: If traffic exceeds the moving average by `2.5x` (`BURST_THRESHOLD_MULTIPLIER`), it marks a burst event (`ORANGE`).

### C. Anomaly Detector (`detection/anomaly_detector.py`)
Uses Shannon Entropy to measure the randomness of source IP distributions:
$$H(X) = - \sum_{i=1}^n P(x_i) \log_2 P(x_i)$$
* **Entropy Anomaly**: Lower entropy signifies high concentration from fewer IPs (e.g. target flood). If entropy falls below `1.2 bits` (`ENTROPY_IP_THRESHOLD`), the engine raises a `RED` alert for a targeted flood attack.

---

## 5. Mitigation Engine (`mitigation/`)

Mitigation filters incoming traffic based on three rulesets:

### A. Blacklist Manager (`mitigation/blacklist_manager.py`)
Manages temporary or permanent IP blocks.
* If a blocked IP tries to connect, the TCP socket is immediately dropped at the listener stage.
* **Auto-Aging/Expiration**: A background checker automatically lifts expired blocks and logs `LIFT_LIMIT` actions.

### B. Concurrency Limiter (`mitigation/connection_limiter.py`)
* Restricts concurrent TCP connections per IP to a maximum of **8** (`max_concurrent_connections`).
* Exceeding this limit drops connections and (under `automatic` mode) triggers a **60-second** IP blacklist block.

### C. Rate Limiter (`mitigation/rate_limiter.py`)
* Employs sliding-window tracking per IP.
* Restricts requests to a maximum of **15 requests/second** (`requests_per_second_limit`).
* Exceeding this threshold responds with `429 Too Many Requests` and (under `automatic` mode) triggers a **30-second** IP blacklist block.

---

## 6. Real-Time Telemetry & Front-End UI

* **Backend Orchestration**: `app.py` serves the Flask web application, coordinates Socket.IO broadcasts (`/stats` namespace) containing CPU/Memory, network I/O, latencies, alerts, and firewall statuses every second.
* **Dynamic Console-Only Dashboard**: A highly polished, responsive dashboard presenting active simulation status, live terminal log feeds colored by source subsystem (Green for Target Server, Red for Alert/DDoSDetector, Orange for Firewall), and control APIs.
* **PDF Report Builder**: Integrates ReportLab to compile experiment charts, metric aggregations, system overhead, and detection accuracy into printable PDF reports.
