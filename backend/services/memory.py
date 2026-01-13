import sqlite3
import time
from collections import Counter

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
    
    # Table for detections with source column
    # If table exists from previous version, we might need to migrate
    # For now, we'll try to create it with the new schema. 
    # If it exists, we will try to add the column (ignoring error if it exists)
    c.execute('''CREATE TABLE IF NOT EXISTS detections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp REAL,
                  label TEXT,
                  confidence REAL,
                  source TEXT DEFAULT 'webcam')''')
    
    try:
        c.execute("ALTER TABLE detections ADD COLUMN source TEXT DEFAULT 'webcam'")
    except sqlite3.OperationalError:
        pass # Column likely already exists
        
    conn.commit()
    conn.close()

def log_sensor_data(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO sensors (timestamp, temperature, humidity, soil_moisture) VALUES (?, ?, ?, ?)",
              (time.time(), 
               data.get('temperature', 0).replace('°C',''), 
               data.get('humidity', 0).replace('%',''), 
               data.get('soil_moisture', 0).replace('%','')))
    conn.commit()
    conn.close()

def log_detection(label, confidence, source="webcam"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO detections (timestamp, label, confidence, source) VALUES (?, ?, ?, ?)",
              (time.time(), label, confidence, source))
    conn.commit()
    conn.close()

def clear_logs():
    """
    Clear all logs from the database for demo reset.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM detections")
    c.execute("DELETE FROM sensors")
    try:
        c.execute("DELETE FROM sqlite_sequence WHERE name='detections'")
        c.execute("DELETE FROM sqlite_sequence WHERE name='sensors'")
    except:
        pass
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

def get_detections_summary(seconds=60):
    """
    Get summary of detections in the last N seconds.
    Returns: { 'most_frequent': 'Blight', 'count': 5, 'last_seen': 'Blight' }
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    cutoff = time.time() - seconds
    c.execute("SELECT label, timestamp FROM detections WHERE timestamp > ? ORDER BY id DESC", (cutoff,))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return {"most_frequent": None, "count": 0, "last_seen": None}
        
    labels = [r['label'] for r in rows]
    last_seen = labels[0]
    
    if not labels:
        return {"most_frequent": None, "count": 0, "last_seen": None}
        
    counter = Counter(labels)
    most_common = counter.most_common(1)[0]
    
    return {
        "most_frequent": most_common[0],
        "count": most_common[1],
        "last_seen": last_seen,
        "total_detections": len(labels)
    }

# Initialize on module load
init_db()
