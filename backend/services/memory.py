import sqlite3
import json
import time

DB_PATH = "agri.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Table for sensor data
    c.execute('''CREATE TABLE IF NOT EXISTS sensors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp REAL,
                  temperature REAL,
                  humidity REAL,
                  soil_moisture REAL)''')
    
    # Table for detections
    c.execute('''CREATE TABLE IF NOT EXISTS detections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp REAL,
                  label TEXT,
                  confidence REAL)''')
    conn.commit()
    conn.close()

def log_sensor_data(data):
    """
    data: dict {temperature, humidity, soil_moisture}
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO sensors (timestamp, temperature, humidity, soil_moisture) VALUES (?, ?, ?, ?)",
              (time.time(), data.get('temperature', 0).replace('°C',''), data.get('humidity', 0).replace('%',''), data.get('soil_moisture', 0).replace('%','')))
    conn.commit()
    conn.close()

def log_detection(label, confidence):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO detections (timestamp, label, confidence) VALUES (?, ?, ?)",
              (time.time(), label, confidence))
    conn.commit()
    conn.close()

def get_latest_sensors():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM sensors ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_recent_detections(limit=5):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM detections ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize on module load (or call explicitly)
init_db()
