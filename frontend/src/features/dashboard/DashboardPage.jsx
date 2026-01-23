import React, { useState } from 'react';
import VideoFeed from '../../components/VideoFeed';
import DetectionLog from '../../components/DetectionLog';
import SensorPanel from '../sensors/SensorPanel';
import WeatherWidget from './components/WeatherWidget';

const DashboardPage = () => {
    // We could add global dashboard state here if needed

    return (
        <div className="dashboard-page" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Top Row: Visuals + Weather */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
                <div style={{ background: 'white', padding: '10px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
                    <VideoFeed />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <WeatherWidget />
                    <SensorPanel />
                </div>
            </div>

            {/* Bottom Row: Logs */}
            <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
                <h3 style={{ margin: '0 0 15px 0', color: '#444' }}>Recent Activity Log</h3>
                <DetectionLog />
            </div>
        </div>
    );
};

export default DashboardPage;
