# backend/memory.py

conversation_history = []


def save_memory(user_query, response):
    conversation_history.append({
        "query": user_query,
        "response": response
    })


def get_memory():
    return conversation_history[-5:]  # last 5 interactions