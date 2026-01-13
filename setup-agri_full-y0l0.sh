#!/bin/bash
# setup_agri_full_yolo.sh
# Full setup: backend (YOLO crop/weed/pest, MQTT, sensors) + frontend React

echo "✅ Starting full Agri Monitoring setup with YOLO crop/weed/pest..."

PROJECT_DIR=~/agri_monitoring
BACKEND_DIR=$PROJECT_DIR/backend
FRONTEND_DIR=$PROJECT_DIR/frontend

# 1) Create folders
mkdir -p $BACKEND_DIR
mkdir -p $FRONTEND_DIR
echo "✅ Folders created"

# 2) Install MQTT broker
brew install mosquitto
brew services start mosquitto
echo "✅ MQTT broker installed"

# 3) Backend setup
cd $BACKEND_DIR
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install flask flask_sqlalchemy paho-mqtt opencv-python ultralytics torch numpy
echo "✅ Python environment and packages installed"

# 4) Backend app.py (YOLO custom model)
cat > $BACKEND_DIR/app.py << 'EOF'
import cv2
from ultralytics import YOLO
from flask import Flask, Response, jsonify
import threading, time, sqlite3
import paho.mqtt.client as mqtt
import random, os

# YOLO model (replace with your custom trained best.pt)
MODEL_PATH = "best.pt"
CAM_SOURCE = 0
DB_PATH = "detections.db"
MQTT_BROKER = "localhost"
MQTT_TOPIC = "agri/alerts"

app = Flask(__name__)
frame_lock = threading.Lock()
latest_frame = None
stop_event = threading.Event()

# Database
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs
             (timestamp TEXT, label TEXT, confidence REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS sensors
             (timestamp TEXT, temperature REAL, humidity REAL, soil_moisture REAL)''')
conn.commit()

# MQTT client
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_start()

# Sensor data
sensor_data = {"temperature":25, "humidity":50, "soil_moisture":30}

def simulate_sensors():
    while not stop_event.is_set():
        sensor_data["temperature"] = round(20 + random.random()*10,1)
        sensor_data["humidity"] = round(40 + random.random()*20,1)
        sensor_data["soil_moisture"] = round(25 + random.random()*30,1)
        c.execute("INSERT INTO sensors VALUES (datetime('now'), ?, ?, ?)",
                  (sensor_data["temperature"], sensor_data["humidity"], sensor_data["soil_moisture"]))
        conn.commit()
        time.sleep(5)

# Load YOLO custom model
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Please put your trained YOLO model {MODEL_PATH} in this folder!")
model = YOLO(MODEL_PATH)

# Webcam capture
def capture_loop():
    global latest_frame
    cap = cv2.VideoCapture(CAM_SOURCE)
    if not cap.isOpened():
        print("❌ Cannot access webcam")
        return
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            continue
        results = model.predict(frame, conf=0.5, verbose=False)
        annotated = results[0].plot() if results else frame
        if results:
            for det in results[0].boxes.data.tolist():
                label = results[0].names[int(det[5])]
                conf = float(det[4])
                c.execute("INSERT INTO logs VALUES (datetime('now'), ?, ?)", (label, conf))
                conn.commit()
                mqtt_client.publish(MQTT_TOPIC, f"{label} detected ({conf:.2f})")
        with frame_lock:
            latest_frame = annotated.copy()
    cap.release()

thread_capture = threading.Thread(target=capture_loop, daemon=True)
thread_capture.start()
thread_sensors = threading.Thread(target=simulate_sensors, daemon=True)
thread_sensors.start()

def generate_mjpeg():
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            ret, jpeg = cv2.imencode('.jpg', latest_frame)
            data = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
        time.sleep(0.03)

@app.route('/')
def index():
    return 'Agri Monitoring Dashboard - /video_feed /logs /sensors'

@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
def logs():
    c.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 20")
    return jsonify(c.fetchall())

@app.route('/sensors')
def sensors():
    return jsonify(sensor_data)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    stop_event.set()
    return "Shutting down..."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
EOF

echo "✅ Backend app.py ready (YOLO custom model)"

# 5) Frontend setup
cd $FRONTEND_DIR
npx create-react-app . > /dev/null 2>&1
npm install axios chart.js react-chartjs-2

mkdir -p src/components

# VideoFeed
cat > src/components/VideoFeed.js << 'EOF'
import React from 'react';
const VideoFeed = () => (
  <div>
    <h2>Live Webcam Feed</h2>
    <img src="http://localhost:5000/video_feed" alt="Live feed"/>
  </div>
);
export default VideoFeed;
EOF

# DetectionLog
cat > src/components/DetectionLog.js << 'EOF'
import React,{useEffect,useState} from 'react';
import axios from 'axios';
const DetectionLog = () => {
  const [logs,setLogs]=useState([]);
  useEffect(()=>{
    const interval=setInterval(()=>{axios.get('http://localhost:5000/logs').then(res=>setLogs(res.data))},2000);
    return ()=>clearInterval(interval);
  },[]);
  return (<div>
    <h2>Detection Logs</h2>
    <ul>{logs.map((l,i)=><li key={i}>{l[0]} - {l[1]} ({l[2].toFixed(2)})</li>)}</ul>
  </div>);
};
export default DetectionLog;
EOF

# Sensors component
cat > src/components/Sensors.js << 'EOF'
import React,{useEffect,useState} from 'react';
import axios from 'axios';
const Sensors = () => {
  const [data,setData]=useState({temperature:0,humidity:0,soil_moisture:0});
  useEffect(()=>{
    const interval=setInterval(()=>{axios.get('http://localhost:5000/sensors').then(res=>setData(res.data))},2000);
    return ()=>clearInterval(interval);
  },[]);
  return (<div>
    <h2>Sensor Data</h2>
    <ul>
      <li>Temperature: {data.temperature} °C</li>
      <li>Humidity: {data.humidity} %</li>
      <li>Soil Moisture: {data.soil_moisture} %</li>
    </ul>
  </div>);
};
export default Sensors;
EOF

# App.js
cat > src/App.js << 'EOF'
import VideoFeed from './components/VideoFeed';
import DetectionLog from './components/DetectionLog';
import Sensors from './components/Sensors';
function App() {
  return (
    <div>
      <VideoFeed/>
      <DetectionLog/>
      <Sensors/>
    </div>
  );
}
export default App;
EOF

echo "✅ Frontend React app created"

echo "🎉 Full YOLO crop/weed/pest setup complete!"
echo "Steps to run:"
echo "1) Copy your trained best.pt into ~/agri_monitoring/backend/"
echo "2) Run backend:"
echo "   cd ~/agri_monitoring/backend"
echo "   source .venv/bin/activate"
echo "   python app.py"
echo "3) Run frontend:"
echo "   cd ~/agri_monitoring/frontend"
echo "   npm start"
echo "4) Open http://localhost:3000 to see live webcam + detection logs + sensors"
echo "5) Subscribe to MQTT topic 'agri/alerts' to see detection notifications"
