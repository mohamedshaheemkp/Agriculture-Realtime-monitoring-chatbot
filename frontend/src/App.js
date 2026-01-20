import React from "react";
import Dashboard from "./features/dashboard/DashboardPage";
import Chatbot from "./features/chatbot/Chatbot";
import UploadImage from "./features/vision/UploadImage";
import './App.css';

function App() {
  return (
    <div className="App">
      <Dashboard />
      <div className="interactive-section">
        <Chatbot />
        <UploadImage />
      </div>
    </div>
  );
}

export default App;
