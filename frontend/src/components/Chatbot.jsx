import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../config';

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { sender: 'user', text: input };
        setMessages([...messages, userMsg]);

        try {
            const res = await axios.post(`${API_URL}/chat`, { message: input });
            const botMsg = { sender: 'bot', text: res.data.response };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error("Chat error", error);
        }
        setInput('');
    };

    return (
        <div className="chatbot">
            <h2>AI Agri-Advisor</h2>
            <div className="chat-window">
                {messages.map((m, i) => (
                    <div key={i} className={`message ${m.sender}`}>
                        {m.text}
                    </div>
                ))}
            </div>
            <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask about crops..."
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
};

export default Chatbot;
