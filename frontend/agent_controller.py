# frontend/agent_controller.py

import re

def decide_tool(query: str):
    query = query.lower()

    # 🔢 Calculator detection
    math_patterns = [
        r"\d+\s*[\+\-\*\/]\s*\d+",   # basic math
        r"calculate",
        r"what is \d",
    ]
    
    for pattern in math_patterns:
        if re.search(pattern, query):
            return "calculator"

    # 🌐 Web search detection
    web_keywords = [
        "latest", "news", "today", "current", "recent"
    ]
    
    for word in web_keywords:
        if word in query:
            return "web"

    # 📄 Default → RAG
    return "rag"