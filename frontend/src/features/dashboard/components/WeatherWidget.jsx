import React, { useEffect, useState } from 'react';
import { weatherService } from '../../../services/sensorService';

const WeatherWidget = () => {
    const [weather, setWeather] = useState(null);

    useEffect(() => {
        const fetchWeather = async () => {
            // Can pass lat/lon if GPS available
            const data = await weatherService.getCurrentWeather();
            setWeather(data);
        };
        fetchWeather();
    }, []);

    if (!weather) return <div style={{ padding: '20px', background: 'white', borderRadius: '12px' }}>Loading Weather...</div>;

    const isAlert = !!weather.forecast_alert;

    return (
        <div style={{
            background: isAlert ? '#fffde7' : 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)',
            color: isAlert ? '#333' : 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            border: isAlert ? '1px solid #fbc02d' : 'none'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{weather.location}</h3>
                    <p style={{ margin: '5px 0 0 0', opacity: 0.9 }}>{weather.condition}</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold', lineHeight: 1 }}>{Math.round(weather.temp_c)}°</div>
                </div>
            </div>

            <div style={{ marginTop: '20px', display: 'flex', gap: '15px', fontSize: '0.9rem', opacity: 0.9 }}>
                <span>💧 {weather.humidity_pct}% Humidity</span>
                <span>💨 {weather.wind_kph} km/h</span>
            </div>

            {isAlert && (
                <div style={{
                    marginTop: '15px',
                    padding: '8px',
                    background: '#fff9c4',
                    color: '#f57f17',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px'
                }}>
                    ⚠️ {weather.forecast_alert}
                </div>
            )}
        </div>
    );
};

export default WeatherWidget;
