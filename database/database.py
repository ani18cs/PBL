import sqlite3
import os

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "ddos_platform.db")

def get_connection():
    """Returns a connection to SQLite database with timeout handling."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    # Enable dictionary row factory
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates SQLite tables if they do not exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Create experiments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        start_time REAL NOT NULL,
        end_time REAL,
        configuration TEXT NOT NULL
    );
    """)

    # 2. Create system_metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        cpu_usage REAL NOT NULL,
        memory_usage REAL NOT NULL,
        disk_usage REAL NOT NULL,
        network_in REAL NOT NULL,
        network_out REAL NOT NULL
    );
    """)

    # 3. Create traffic_metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS traffic_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        requests_per_second INTEGER NOT NULL,
        active_connections INTEGER NOT NULL,
        average_latency REAL NOT NULL
    );
    """)

    # 4. Create connection_history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS connection_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        source_ip TEXT NOT NULL,
        request_count INTEGER NOT NULL,
        connection_count INTEGER NOT NULL,
        average_latency REAL NOT NULL
    );
    """)

    # 5. Create alerts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        source_ip TEXT
    );
    """)

    # 6. Create mitigation_actions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mitigation_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        action TEXT NOT NULL,
        target TEXT NOT NULL,
        duration INTEGER
    );
    """)
    
    conn.commit()
    conn.close()
    print("[Database] SQLite database initialized successfully.")

if __name__ == "__main__":
    init_db()
