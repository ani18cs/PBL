import time
import json
from database.database import get_connection

class ExperimentModel:
    @staticmethod
    def start_experiment(name, config_dict):
        conn = get_connection()
        cursor = conn.cursor()
        now = time.time()
        config_str = json.dumps(config_dict)
        cursor.execute(
            "INSERT INTO experiments (name, start_time, configuration) VALUES (?, ?, ?)",
            (name, now, config_str)
        )
        exp_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return exp_id

    @staticmethod
    def stop_experiment(exp_id):
        conn = get_connection()
        cursor = conn.cursor()
        now = time.time()
        cursor.execute(
            "UPDATE experiments SET end_time = ? WHERE id = ?",
            (now, exp_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experiments ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

class SystemMetricsModel:
    @staticmethod
    def log_metrics(cpu, memory, disk, net_in, net_out):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO system_metrics (timestamp, cpu_usage, memory_usage, disk_usage, network_in, network_out) VALUES (?, ?, ?, ?, ?, ?)",
            (time.time(), cpu, memory, disk, net_in, net_out)
        )
        conn.commit()
        conn.close()

class TrafficMetricsModel:
    @staticmethod
    def log_metrics(requests_sec, active_conns, avg_latency):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO traffic_metrics (timestamp, requests_per_second, active_connections, average_latency) VALUES (?, ?, ?, ?)",
            (time.time(), requests_sec, active_conns, avg_latency)
        )
        conn.commit()
        conn.close()

class ConnectionHistoryModel:
    @staticmethod
    def log_history(source_ip, req_count, conn_count, avg_latency):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO connection_history (timestamp, source_ip, request_count, connection_count, average_latency) VALUES (?, ?, ?, ?, ?)",
            (time.time(), source_ip, req_count, conn_count, avg_latency)
        )
        conn.commit()
        conn.close()

class AlertModel:
    @staticmethod
    def trigger_alert(severity, description, source_ip=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts (timestamp, severity, description, source_ip) VALUES (?, ?, ?, ?)",
            (time.time(), severity, description, source_ip)
        )
        conn.commit()
        conn.close()

class MitigationActionModel:
    @staticmethod
    def log_action(action, target, duration=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mitigation_actions (timestamp, action, target, duration) VALUES (?, ?, ?, ?)",
            (time.time(), action, target, duration)
        )
        conn.commit()
        conn.close()
