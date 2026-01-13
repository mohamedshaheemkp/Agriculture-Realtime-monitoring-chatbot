import React, { useEffect, useState } from "react";
import axios from "axios";

export default function DetectionLog() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await axios.get("http://localhost:5050/logs");
        setLogs(response.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 3000); // refresh every 3s
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>Detection Logs</h2>
      <ul>
        {logs.map((log, idx) => (
          <li key={idx}>{log}</li>
        ))}
      </ul>
    </div>
  );
}

