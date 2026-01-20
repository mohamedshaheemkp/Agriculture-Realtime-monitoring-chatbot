import React, { useState, useRef, useEffect } from 'react';
import { chatbotService } from '../../services/chatbotService';
import styles from '../../styles/Chatbot.module.css';

const Chatbot = () => {
    const [messages, setMessages] = useState([
        { sender: 'bot', text: 'Hello! I am your Agri-Assistant. Ask me about your crop health or current alerts.' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userText = input;
        setInput('');

        // Add User Message
        setMessages(prev => [...prev, { sender: 'user', text: userText }]);
        setIsTyping(true);

        try {
            const data = await chatbotService.sendMessage(userText);
            setMessages(prev => [...prev, { sender: 'bot', text: data.reply }]);
        } catch (error) {
            setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I'm having trouble connecting to the server." }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.header}>
                <span>AI Agri-Advisor</span>
                <span className={styles.statusIndicator} title="Online"></span>
            </div>

            <div className={styles.messagesArea}>
                {messages.map((m, i) => (
                    <div key={i} className={`${styles.messageBubble} ${m.sender === 'user' ? styles.userMsg : styles.botMsg}`}>
                        {m.text}
                    </div>
                ))}
                {isTyping && <div className={styles.typing}>Thinking...</div>}
                <div ref={messagesEndRef} />
            </div>

            <div className={styles.inputArea}>
                <input
                    className={styles.inputField}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask a question..."
                    disabled={isTyping}
                />
                <button
                    className={styles.sendButton}
                    onClick={handleSend}
                    disabled={!input.trim() || isTyping}
                >
                    ➔
                </button>
            </div>
        </div>
    );
};

export default Chatbot;
