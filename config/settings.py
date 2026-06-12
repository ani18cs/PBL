import os

# Base paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "database", "ddos_platform.db")

# Server settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
