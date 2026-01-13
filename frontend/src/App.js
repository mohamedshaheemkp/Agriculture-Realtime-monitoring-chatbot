import React from "react";
import Dashboard from "./components/Dashboard";
import Chatbot from "./components/Chatbot";
import UploadImage from "./components/UploadImage";
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
