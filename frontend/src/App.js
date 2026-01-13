import React from "react";
import VideoFeed from "./VideoFeed";
import DetectionLog from "./DetectionLog";
import Sensors from "./Sensors";

function App() {
  return (
    <div className="App" style={{ textAlign: "center", fontFamily: "Arial" }}>
      <h1>Real-Time Agri Monitoring</h1>
      <VideoFeed />
      <DetectionLog />
      <Sensors />
    </div>
  );
}

export default App;
