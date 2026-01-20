import axios from 'axios';
import { API_URL } from '../config';

const api = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' }
});

export const chatbotService = {
    sendMessage: async (message) => {
        try {
            // Updated endpoint to match new backend
            const response = await api.post('/api/v1/chat/message', { message });
            // Unpack standard envelope
            return response.data.data;
        } catch (error) {
            console.error("Chat API Error:", error);
            throw error.response ? error.response.data : error;
        }
    }
};
