# 🛡️ DEFCON-D: DDoS Simulation, Detection, and Mitigation Platform

DEFCON-D is an educational cybersecurity analytics platform designed to demonstrate target server performance drops under load, anomaly-based DDoS detection metrics, and mitigation rules deployment in a safe and authorized lab environment.

> [!WARNING]
> **Defensive Security & Educational Use Only**
> This tool is strictly for educational research, defensive security training, and lab performance testing. It includes safety guardrails preventing requests targeting any external public IP domains.

---

## 🚀 Installation & Getting Started

### Method A: Local Python Execution

1. **Clone the workspace** and navigate to the project root:
   ```bash
   cd ddos_platform
   ```

2. **Create a Python virtual environment** (Python 3.12+ recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application entrypoint**:
   ```bash
   python app.py
   ```
   *The target TCP server will start on port `8080`, and the SocketIO dashboard will run on `http://127.0.0.1:5000`.*

### Method B: Docker Container Deployment

Build and orchestrate the platform using Docker Compose:

```bash
docker-compose up --build
```
*This launches the platform in a bridged Docker network, mapping port `5000` (UI) and port `8080` (TCP Server).*

---

## 📐 System Architecture

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

### SQLite Tables Schema

* **`experiments`**: Logs experiment configuration details (concurrency, intervals, metadata).
* **`system_metrics`**: Records cpu, ram, disk, and network I/O bytes sampled every 1 second.
* **`traffic_metrics`**: Registers request counts, latencies, and connection pools counts.
* **`connection_history`**: Tracks request counts and average latency grouped by client IP.
* **`alerts`**: anomaly alerts (Green, Yellow, Orange, Red) and identified source IPs.
* **`mitigation_actions`**: Blocks, rate limits, and unblock timestamps.

---

## 🔌 API & SocketIO Events Specification

### REST Endpoints

#### 1. Experiment Management
* `GET /api/experiments`: Lists all logged experiments in the database.
* `POST /api/experiments/start`: Starts a simulated profile run.
  - Body: `{"name": "test_run", "profile": "heavy", "duration": 45}`
  - *Profiles available: `normal`, `medium`, `heavy`, `stress`*
* `POST /api/experiments/stop`: Force-stops any currently active simulator loops.

#### 2. Firewall Overrides
* `POST /api/mitigation/block`: Manually blacklists a source IP.
  - Body: `{"ip": "192.168.1.99", "duration": 120}`
* `POST /api/mitigation/unblock`: Removes a blacklist rule.
  - Body: `{"ip": "192.168.1.99"}`
* `POST /api/mitigation/mode`: Switches mitigation state rules.
  - Body: `{"mode": "automatic"}`  # Options: `automatic`, `manual`, `hybrid`

#### 3. PDF Summary Reports
* `GET /api/reports`: Lists available reports directory metadata.
* `GET /api/reports/download/<int:exp_id>`: Compiles and downloads the PDF report for experiment `exp_id`.

### Real-Time WebSocket Channel (`/stats` namespace)

Listens for the `metrics_update` broadcast event emitting the following JSON payload every second:
```json
{
  "timestamp": "20:30:15",
  "cpu": 12.5,
  "memory": 45.8,
  "disk": 10.2,
  "network_in": 5120,
  "network_out": 2048,
  "requests_per_second": 100,
  "active_connections": 12,
  "average_latency": 1.25,
  "severity": "RED",
  "blocked_ips": [{"ip": "192.168.1.99", "remaining": 28}],
  "mode": "automatic",
  "active_experiment": "test_run"
}
```

---

## 🧪 Running Unit & Integration Tests

The test suite provides complete validation covering socket transactions, entropy alarms, sliding-window rate limiters, and ReportLab PDF compilers. Run the tests using python's test discover utility:

```bash
python -m unittest discover tests
```
*Current test suite coverage: 11 tests, 100% pass rate.*
