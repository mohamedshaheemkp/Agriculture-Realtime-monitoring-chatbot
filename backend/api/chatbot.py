def get_chat_response(message):
    # Placeholder for chatbot logic
    # Could connect to LLM or rule-based system
    if "tomato" in message.lower():
        return "Tomato plants need consistent watering and full sun. Watch out for blight."
    elif "pest" in message.lower():
        return "Common pests include aphids and mites. Neem oil is a good organic remedy."
    else:
        return "I can help with agricultural queries. Ask me about your crops!"
