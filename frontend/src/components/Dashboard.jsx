import React, { useEffect, useState } from 'react';
import axios from 'axios';
import VideoFeed from './VideoFeed';
import Sensors from './Sensors';
import DetectionLog from './DetectionLog';

function Dashboard() {
    const [activeTab, setActiveTab] = useState('live');

    return (
        <div className="dashboard-container">
            <h1>Agri Monitoring Dashboard</h1>
            <div className="tabs">
                <button onClick={() => setActiveTab('live')}>Live Monitoring</button>
                <button onClick={() => setActiveTab('logs')}>Logs</button>
            </div>

            <div className="content">
                <div className="main-panel">
                    <VideoFeed />
                </div>
                <div className="side-panel">
                    <Sensors />
                    <DetectionLog />
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
