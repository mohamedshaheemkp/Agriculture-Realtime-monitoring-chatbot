import axios from 'axios';
import { API_URL } from '../config';

const api = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' }
});

export const sensorService = {
    getTelemetry: async () => {
        try {
            const response = await api.get('/api/v1/sensors/telemetry');
            return response.data.data;
        } catch (error) {
            console.error("Sensor API Error:", error);
            return null;
        }
    }
};

export const weatherService = {
    getCurrentWeather: async (lat, lon) => {
        try {
            const params = lat && lon ? { lat, lon } : {};
            const response = await api.get('/api/v1/weather/current', { params });
            return response.data.data;
        } catch (error) {
            console.error("Weather API Error:", error);
            return null;
        }
    }
};
