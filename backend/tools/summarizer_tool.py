# backend/tools/summarizer_tool.py

import ollama
from backend.config import OLLAMA_MODEL
from backend.rag_pipeline import (
    load_all,
    hybrid_retrieve
)

# ======================================
# 🔹 LOAD RAG COMPONENTS ONCE
# ======================================

vectorstore, bm25, texts = load_all()


# ======================================
# 🔹 LLM HELPER
# ======================================

def ask_llm(prompt: str):

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# ======================================
# 🔹 SUMMARIZER TOOL
# ======================================

def summarizer_tool(query: str, k: int = 5):

    # 🔹 Retrieve relevant documents
    docs = hybrid_retrieve(
        query=query,
        vectorstore=vectorstore,
        bm25=bm25,
        texts=texts,
        k=k
    )

    # 🔹 Combine context
    context = "\n\n".join(docs)

    # 🔹 Summarization prompt
    prompt = f"""
    You are an intelligent summarization assistant.

    Summarize the following content clearly and concisely.

    Focus on:
    - key points
    - important concepts
    - meaningful insights

    Content:
    {context}

    Provide a structured summary.
    """

    summary = ask_llm(prompt)

    return {
        "tool": "SUMMARIZER",
        "query": query,
        "summary": summary
    }