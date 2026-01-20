import axios from 'axios';
import { API_URL } from '../config';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const visionService = {
    analyzeImage: async (file) => {
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await api.post('/api/v1/vision/analyze', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            // Unpack standard envelope
            return response.data.data;
        } catch (error) {
            console.error("Vision API Error:", error);
            throw error.response ? error.response.data : error;
        }
    },

    getHistory: async () => {
        try {
            const response = await api.get('/api/v1/vision/history');
            return response.data.data;
        } catch (error) {
            console.error("History API Error:", error);
            return [];
        }
    }
};
