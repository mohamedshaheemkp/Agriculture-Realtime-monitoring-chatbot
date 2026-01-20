import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_URL } from "../config";

export default function VideoFeed() {
  const [currentDisplay, setCurrentDisplay] = useState([]);

  useEffect(() => {
    // Poll for the "current frame" detection (for immediate overlay feedback separate from logs)
    const fetchCurrent = async () => {
      try {
        const res = await axios.get(`${API_URL}/logs`);
        setCurrentDisplay(res.data);
      } catch (e) { console.error(e); }
    };

    const interval = setInterval(fetchCurrent, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="video-feed-container">
      <h2>Live Webcam Feed</h2>
      <div className="video-wrapper">
        <img
          src={`${API_URL}/video_feed`}
          alt="Live feed"
          className="video-stream"
        />
        {currentDisplay.length > 0 && (
          <div className="video-overlay">
            {currentDisplay.map((txt, i) => <div key={i}>{txt}</div>)}
          </div>
        )}
      </div>
    </div>
  );
}
