import React from "react";

export default function VideoFeed() {
  return (
    <div>
      <h2>Live Webcam Feed</h2>
      <img
        src="http://localhost:5050/video_feed"
        alt="Live feed"
        style={{ width: "640px", height: "480px", border: "2px solid black" }}
      />
    </div>
  );
}
