# 🛡️ DEFCON-D DDoS Platform: A-Z Reference and System Architecture Manual

This document provides a comprehensive, deep-dive reference detailing how every component, backend system, telemetry pipeline, and mathematical model works in the **DEFCON-D DDoS Simulation, Detection, and Mitigation Platform**.

---

## 1. System Overview & Educational Objectives

DEFCON-D is an educational cyber-range designed to safely simulate real-world Distributed Denial of Service (DDoS) scenarios, perform real-time anomaly-based traffic analysis, and evaluate reactive mitigation policies. 

### Core Pedagogical Goals:
* **Simulate Load Profiles**: Model difference in system impact between legitimate user traffic and high-volume attacks (concurrency, PPS).
* **Observe Metric Spikes**: Highlight the correlation between traffic floods and target system health (CPU, memory, packet processing latencies).
* **Deploy Mathematical Detection**: Demonstrate how basic statistical filters (PPS rate and burst) combined with info-theoretic models (Shannon Entropy) detect concentrated attacks.
* **Observe Mitigation States**: Study the effectiveness of automated firewalls (sliding-window rate limiters, connection limiters, and temporary blocklists).

---

## 2. Request Lifecycle & Pipeline Architecture

The workflow below details how a single simulated request passes through the socket handlers, gets evaluated against active mitigation rules, gets measured for telemetry, and is ultimately analyzed by the detection engine.

```
+-----------------------------------------------------------------------------------+
| 1. TRAFFIC SIMULATION                                                             |
|    TrafficGenerator spawner -> TCP Connection -> client_ip                        |
+-----------------------------------------------------------------------------------+
                                         |
                                         V
+-----------------------------------------------------------------------------------+
| 2. TCP SERVER ACCEPTANCE & FIREWALL FILTER (TargetServer._listen_loop)            |
|    Checks BlacklistManager.is_blocked(client_ip)                                  |
|    - Yes: Instantly drops TCP Socket                                              |
|    - No: Enters Concurrency Limiter                                               |
+-----------------------------------------------------------------------------------+
                                         |
                                         V
+-----------------------------------------------------------------------------------+
| 3. CONCURRENCY LIMIT REGISTRATION (ConnectionLimiter)                             |
|    Active connection count for IP incremented                                     |
|    - Exceeds Limit: Returns False, Triggers Auto-Block (60s), drops socket       |
|    - Allowed: Spawns ClientHandler Thread                                         |
+-----------------------------------------------------------------------------------+
                                         |
                                         V
+-----------------------------------------------------------------------------------+
| 4. REQUEST RATE EVALUATION (RateLimiter)                                          |
|    Parses HTTP payload. Filters sliding window timestamps for IP (last 1.0s)      |
|    - Exceeds Limit (15 req/s): Responds with 429, Auto-Blocks (30s)               |
|    - Allowed: Responds 200 OK, tracks latency delta                               |
+-----------------------------------------------------------------------------------+
                                         |
                                         V
+-----------------------------------------------------------------------------------+
| 5. TELEMETRY AGGREGATION & TERMINATION (ConnectionManager)                        |
|    Decrements concurrency count on socket close. Logs request speed/latency.      |
+-----------------------------------------------------------------------------------+
                                         |
                                         V
+-----------------------------------------------------------------------------------+
| 6. SECONDS MONITORING & DDOS DETECTION ENGINE                                     |
|    Daemon polls ConnectionManager. Computes:                                      |
|    - PPS Rate (Green/Yellow/Red alerts)                                           |
|    - 10s Moving Average Burst (Orange alerts)                                     |
|    - Shannon Entropy of IPs (Low Entropy = Red targeted flood)                    |
+-----------------------------------------------------------------------------------+
                                         |
                                         V
+-----------------------------------------------------------------------------------+
| 7. LOGS AND VISUALIZATION                                                         |
|    Writes stats to SQLite DB. Broadcasts payload over Socket.IO to Console.       |
+-----------------------------------------------------------------------------------+
```

---

## 3. Backend System Reference Guide

### A. Target TCP Server (`server/`)
* **`server/target_server.py`**:
  * Initializes the listening socket (`socket.listen(128)`) on port `8080`.
  * Runs `listener_thread` executing a continuous `accept()` loop. When mitigation checks pass, it spawns `handle_client_socket` in a daemonized thread to process the HTTP transaction asynchronously.
  * Runs `monitor_thread` which wakes up every `1.0` seconds, drains the aggregate connection statistics window, commits metrics/IP histories to SQLite, and prints runtime state updates.
* **`server/connection_manager.py`**:
  * Features a thread-safe registry (`threading.Lock()`) tracking connection metrics in sliding windows.
  * `pop_metrics()` aggregates requests per second (PPS), active connections count, and average transaction latency for the telemetry engine, resetting counters for the next 1-second slot.
* **`server/request_handler.py`**:
  * Coordinates parsing of the client payload. If the rate checker blocks the request, it transmits an HTTP `429 Too Many Requests` response. Otherwise, it fulfills the request with an HTTP `200 OK` header, logging connection timings.

### B. Database Models & Schema (`database/`)
The persistence layer manages relational telemetry data:
* **`database/database.py`**: Handles initialization (`init_db()`), establishing the tables and indices.
* **`database/models.py`**: Contains specialized wrappers representing SQL operations:
  * `ExperimentModel`: Creates running experiment records, marking timestamps and serialized profile parameters.
  * `SystemMetricsModel`: Telemetry queries recording operating system status (CPU, memory, disk, network throughput).
  * `TrafficMetricsModel`: High-frequency queries logging requests per second, active connections, and latency logs.
  * `AlertModel`: Logs security alert severity logs, descriptions, and culprit source IPs.
  * `MitigationActionModel`: Stores timestamps and duration properties for automated firewall overrides.

---

## 4. Traffic Simulation & Load Profiles (`simulator/`)

The simulation engine models various load levels, ranging from benign baseline traffic to intense floods.

### A. Traffic Profiles (`simulator/traffic_profiles.py`)
Configurations define thread workers and request intervals:
* **`normal`**: 10 clients executing requests at `0.5s` intervals. Uses `2` thread workers.
* **`medium`**: 30 clients executing requests at `0.2s` intervals. Uses `5` thread workers.
* **`heavy`**: 80 clients executing requests at `0.05s` intervals. Uses `15` thread workers.
* **`stress`**: 150 clients executing requests at `0.01s` intervals. Uses `30` thread workers.

### B. Traffic Generator & Guardrails (`simulator/traffic_generator.py`)
* Uses a `ThreadPoolExecutor` matching profile concurrency limits.
* Simulates randomized source client IPs ranging from `192.168.1.100` upward.
* Applies a random jitter delay to request schedules (`0.8` to `1.2` multiplier of the base profile interval) to prevent synchronous synthetic spikes.
* **Safety Guardrail**: Before initiating socket loops, target hostnames/IPs are parsed against loopback and private subnets (`127.0.0.1`, `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`). External public addresses are immediately blocked, protecting production endpoints.

---

## 5. DDoS Detection Engine Math & Logic

The detection engine evaluates metrics every second to determine threat severity level (`GREEN`, `YELLOW`, `ORANGE`, `RED`).

### A. Rate Analyzer (`detection/rate_analyzer.py`)
Monitors overall requests per second against hard limits:
* $\text{PPS} \ge 50 \implies$ `YELLOW` alert (Suspicious Load).
* $\text{PPS} \ge 150 \implies$ `RED` alert (DDoS Flood).

### B. Burst Detector (`detection/burst_detector.py`)
Compares the current PPS against a moving average compiled over a sliding `BURST_WINDOW_SIZE` (10 seconds):
$$\text{Moving Average} = \frac{1}{N} \sum_{i=1}^{N} \text{PPS}_i$$
If current traffic exceeds the moving average by a factor of $2.5\times$ (`BURST_THRESHOLD_MULTIPLIER`), it indicates a sudden anomaly, triggering an `ORANGE` alert.

### C. Shannon Entropy Detector (`detection/anomaly_detector.py`)
Evaluates the concentration of source IPs using Shannon Entropy:
$$H(X) = - \sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$
Where $P(x_i)$ is the probability of occurrence of IP $x_i$ within the traffic slice.
* **High Entropy (Diverse legitimate traffic)**:
  If $10$ requests come from $10$ distinct client IPs, $P(x_i) = 0.1$ for each IP:
  $$H(X) = - 10 \times (0.1 \times \log_2(0.1)) \approx 3.32 \text{ bits}$$
* **Low Entropy (Targeted attack concentration)**:
  If $10$ requests arrive, with $9$ coming from a single attacker (`192.168.1.100`) and only $1$ from a legitimate user:
  $$P(100) = 0.9, \quad P(101) = 0.1$$
  $$H(X) = - (0.9 \log_2(0.9) + 0.1 \log_2(0.1)) \approx - (0.9 \times (-0.152) + 0.1 \times (-3.322)) \approx 0.47 \text{ bits}$$
  An entropy value below the $1.2\text{ bits}$ threshold (`ENTROPY_IP_THRESHOLD`) triggers a `RED` alert, indicating a targeted DDoS flood.

---

## 6. Mitigation Engine & Simulated Traffic Defense

Mitigation algorithms run with thread synchronization locks (`threading.Lock()`) to handle concurrent requests without race conditions. Since both the simulator and server execute on the same local loopback interface (`127.0.0.1`), the platform implements a specialized request parsing logic to ensure realistic blocking simulations:

### A. Connection-Level Block Handling for Local Traffic
* **Header Parsing**: As TCP sockets initially accept connections from loopback (`127.0.0.1`), the system parses the HTTP `Host:` headers inside the thread handler (`server/request_handler.py`) to discover the client's simulated IP (e.g. `192.168.1.113`).
* **Connection & Blacklist Check**: On the very first request received on a socket, the thread evaluates the simulated IP against active firewall blocklists and connection concurrency limits.
* **Active Blocking & Drop**: If the simulated IP is blacklisted, the socket is immediately closed without sending a response, and the drop event is logged: `[TargetServer] BLOCKED incoming connection from [IP]`.
* **Telemetry Reporting**: Blocked requests are registered in the connection manager as a traffic attempt (`register_blocked_request()`), allowing the dashboard's **Traffic Rate (PPS)** meter to show the full attack volume while displaying blocks.

### B. Sliding-Window Rate Limiting (`mitigation/rate_limiter.py`)
* Keeps a history list of request timestamps for each IP.
* When a request arrives, timestamps older than $1.0\text{ second}$ are dropped:
  $$\text{timestamps} = \{t \mid t_{\text{current}} - t < 1.0\text{s}\}$$
* If the number of remaining timestamps is $\ge 15$, the request is blocked.
* In **Automatic** mode, this rate limit breach triggers an immediate IP blacklist rule.

### C. Dynamic IP Rotation (Attacker Evasion Simulation)
* **IP Rotation on Block**: In `simulator/traffic_generator.py`, when a virtual client connection is closed or dropped by the firewall (returning an empty response or raising a socket exception), the simulator logs the failure status `[---]` and immediately rotates that client's simulated IP to a new random IP in the `192.168.1.100 - 250` range.
* **Realistic Anomaly Flow**: This simulates a dynamic botnet where the firewall detects and blocks an attacker IP, and the attacker instantly transitions to a new source IP to keep flooding the server.

### D. Blacklist Manager & Auto-Aging (`mitigation/blacklist_manager.py`)
Manages temporary or permanent IP blocks.
* **Auto-Aging/Expiration**: A background checker automatically lifts expired blocks and logs `LIFT_LIMIT` actions. When checking `is_blocked()`, if the current time exceeds the unblock timestamp, the IP is removed from the blacklist, a thread is spawned to log `LIFT_LIMIT` in SQLite, and access is restored.

### D. Operational Mitigation Modes
1. **`automatic`**: Blocks rate limit or connection limit offenders automatically (30s and 60s blocks respectively).
2. **`manual`**: Blocks are applied only via API or dashboard request.
3. **`hybrid`**: Triggers rate limit warnings but requires administrative confirmation to block IPs permanently.

---

## 7. Report PDF Generation (`analytics/`)

The Report Compiler (`analytics/report_generator.py`) generates PDF documents using ReportLab Flowables:
1. **Data Gathering**: Queries SQLite databases, pulling metadata, traffic metrics, system logs, alerts, and mitigation events matching the active experiment time window.
2. **Calculations**: Computes peak resource metrics (maximum CPU, RAM, traffic volume, connection count) and average latency.
3. **Formatting Flowables**:
   * Uses `SimpleDocTemplate` to structure page geometry.
   * Compiles experiment metadata and health summaries into clean, grid-aligned PDF Tables.
   * Logs alert lists and firewall overrides using distinct visual highlighting.
   * Appends an automated educational summary review before compiling the document.

---

## 8. WebSockets & Real-Time Dashboard UI

The communication and frontend layer provides a lightweight, real-time command center:
* **Background Telemetry Spawner**: `app.py` runs a background task polling host metrics (via `psutil`) and database status. Every second, it broadcasts a statistics update package via Socket.IO.
* **Socket.IO Event Stream**: The UI listens for `metrics_update` broadcasts in the `/stats` namespace, updating logs and system health status.
* **Console-Only Display**: The interface focuses on a full-width real-time console with custom styling to distinguish different source components:
  * `[TrafficGen]`: Displays virtual client traffic patterns.
  * `[TargetServer]`: Tracks request handling, traffic rates, and active TCP socket metrics.
  * `[DDoSDetector]`: Logs threat evaluations and severity levels.
  * `[Firewall]`: Tracks active firewall overrides, blocked IPs, and auto-aging unblocks.
