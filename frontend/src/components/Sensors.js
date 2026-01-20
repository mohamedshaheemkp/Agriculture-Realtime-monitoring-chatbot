import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_URL } from "../config";

export default function Sensors() {
  const [data, setData] = useState({});

  useEffect(() => {
    const fetchSensors = async () => {
      try {
        const response = await axios.get(`${API_URL}/sensors`);
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
