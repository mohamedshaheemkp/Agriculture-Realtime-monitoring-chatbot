import sqlite3
import logging
from app.core.config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DB_PATH

    def get_connection(self):
        """Creates a database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return dict-like objects
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def init_db(self):
        """Initialize the database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table for sensor data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                temperature REAL,
                humidity REAL,
                soil_moisture REAL
            )
        ''')

        # Table for detections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                label TEXT,
                confidence REAL,
                source TEXT DEFAULT 'webcam'
            )
        ''')
        
        # Check and add column if missing (for migrations)
        try:
            cursor.execute("SELECT source FROM detections LIMIT 1")
        except sqlite3.OperationalError:
            try:
                cursor.execute("ALTER TABLE detections ADD COLUMN source TEXT DEFAULT 'webcam'")
            except Exception:
                pass

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")

# Singleton instance
db = DatabaseManager()
