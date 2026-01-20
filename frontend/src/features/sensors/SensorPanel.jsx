import React, { useEffect, useState } from 'react';
import { sensorService } from '../../services/sensorService';

const SensorPanel = () => {
    const [data, setData] = useState({ temperature: '--', humidity: '--', soil_moisture: '--' });

    useEffect(() => {
        const fetchData = async () => {
            const telemetry = await sensorService.getTelemetry();
            if (telemetry) setData(telemetry);
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (soilVal) => {
        const val = parseFloat(soilVal);
        if (isNaN(val)) return 'gray';
        return val < 20 ? '#e53935' : '#43a047'; // Red if low, Green if good
    };

    return (
        <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
            display: 'flex',
            flexDirection: 'column',
            gap: '15px'
        }}>
            <h3 style={{ margin: 0, color: '#333' }}>Live Sensor Data</h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                <div style={{ textAlign: 'center', padding: '10px', background: '#e3f2fd', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.9rem', color: '#1565c0' }}>Temp</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#0d47a1' }}>{data.temperature}</div>
                </div>

                <div style={{ textAlign: 'center', padding: '10px', background: '#e8f5e9', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.9rem', color: '#2e7d32' }}>Humidity</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#1b5e20' }}>{data.humidity}</div>
                </div>

                <div style={{ textAlign: 'center', padding: '10px', background: '#fff3e0', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.9rem', color: '#ef6c00' }}>Soil Moisture</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#e65100' }}>{data.soil_moisture}</div>
                </div>
            </div>

            <div style={{
                fontSize: '0.85rem',
                color: '#666',
                borderTop: '1px solid #eee',
                paddingTop: '10px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
            }}>
                <span style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: getStatusColor(data.soil_moisture),
                    display: 'inline-block'
                }}></span>
                Status: {parseFloat(data.soil_moisture) < 20 ? "Irrigation Needed" : "Optimal"}
            </div>
        </div>
    );
};

export default SensorPanel;
