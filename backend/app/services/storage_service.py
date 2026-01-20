import time
from collections import Counter
from app.core.database import db

class StorageService:
    def log_sensor_data(self, data):
        conn = db.get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO sensors (timestamp, temperature, humidity, soil_moisture) VALUES (?, ?, ?, ?)",
                    (time.time(), 
                    data.get('temperature', 0).replace('°C',''), 
                    data.get('humidity', 0).replace('%',''), 
                    data.get('soil_moisture', 0).replace('%','')))
            conn.commit()
        finally:
            conn.close()

    def log_detection(self, label, confidence, source="webcam"):
        conn = db.get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO detections (timestamp, label, confidence, source) VALUES (?, ?, ?, ?)",
                    (time.time(), label, confidence, source))
            conn.commit()
        finally:
            conn.close()

    def clear_logs(self):
        """
        Clear all logs from the database for demo reset.
        """
        conn = db.get_connection()
        c = conn.cursor()
        try:
            c.execute("DELETE FROM detections")
            c.execute("DELETE FROM sensors")
            try:
                c.execute("DELETE FROM sqlite_sequence WHERE name='detections'")
                c.execute("DELETE FROM sqlite_sequence WHERE name='sensors'")
            except Exception:
                pass
            conn.commit()
        finally:
            conn.close()

    def get_latest_sensors(self):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM sensors ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def get_recent_detections(self, limit=5):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM detections ORDER BY id DESC LIMIT ?", (limit,))
            rows = c.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_detections_summary(self, seconds=60):
        """
        Get summary of detections in the last N seconds.
        """
        conn = db.get_connection()
        try:
            c = conn.cursor()
            cutoff = time.time() - seconds
            c.execute("SELECT label, timestamp FROM detections WHERE timestamp > ? ORDER BY id DESC", (cutoff,))
            rows = c.fetchall()
            
            if not rows:
                return {"most_frequent": None, "count": 0, "last_seen": None, "total_detections": 0}
                
            labels = [r['label'] for r in rows]
            last_seen = labels[0]
            
            counter = Counter(labels)
            most_common = counter.most_common(1)[0]
            
            return {
                "most_frequent": most_common[0],
                "count": most_common[1],
                "last_seen": last_seen,
                "total_detections": len(labels)
            }
        finally:
            conn.close()

storage_service = StorageService()
