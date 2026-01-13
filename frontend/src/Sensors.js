import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Sensors() {
  const [data, setData] = useState({});

  useEffect(() => {
    const fetchSensors = async () => {
      try {
        const response = await axios.get("http://localhost:5050/sensors");
        setData(response.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchSensors();
    const interval = setInterval(fetchSensors, 5000); // refresh every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>Sensor Data</h2>
      <p>Temperature: {data.temperature}</p>
      <p>Humidity: {data.humidity}</p>
    </div>
  );
}
