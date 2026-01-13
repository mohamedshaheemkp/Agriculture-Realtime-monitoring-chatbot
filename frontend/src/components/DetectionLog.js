import React, { useEffect, useState } from "react";
import axios from "axios";

export default function DetectionLog() {
  const [logs, setLogs] = useState([]);
  const [latestItem, setLatestItem] = useState(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        // Fetch raw history from database
        const response = await axios.get("http://localhost:5050/detections/latest?limit=10");
        const data = response.data;
        setLogs(data);
        if (data.length > 0) {
          setLatestItem(data[0]);
        }
      } catch (err) {
        console.error("Error fetching logs", err);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 1500); // Poll every 1.5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="detection-panel">
      {latestItem && (
        <div className="latest-alert">
          <h3>Latest Detection</h3>
          <div className="alert-box">
            <span className="alert-label">{latestItem.label}</span>
            <span className="alert-conf">{Math.round(latestItem.confidence * 100)}%</span>
          </div>
          <div className="alert-time">
            {new Date(latestItem.timestamp * 1000).toLocaleTimeString()}
          </div>
        </div>
      )}

      <div className="log-list-container">
        <h4>Recent Activity</h4>
        <ul className="log-list">
          {logs.map((log, idx) => (
            <li key={idx} className={idx === 0 ? "log-item latest" : "log-item"}>
              <span className="log-time">
                {new Date(log.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
              <span className="log-label">{log.label}</span>
              <span className="log-source">({log.source})</span>
            </li>
          ))}
          {logs.length === 0 && <li className="log-empty">No detections yet...</li>}
        </ul>
      </div>
    </div>
  );
}
