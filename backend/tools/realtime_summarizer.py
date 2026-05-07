# backend/tools/realtime_summarizer.py

import ollama
from backend.config import OLLAMA_MODEL
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


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
# 🔹 LOAD PDF
# ======================================

def load_pdf(pdf_path):

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    return docs


# ======================================
# 🔹 SPLIT DOCUMENT
# ======================================

def split_docs(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200
    )

    return splitter.split_documents(documents)


# ======================================
# 🔹 SUMMARIZE DOCUMENT
# ======================================

def summarize_uploaded_document(pdf_path):

    # 🔹 Load PDF
    docs = load_pdf(pdf_path)

    # 🔹 Split into chunks
    chunks = split_docs(docs)

    # 🔹 Combine text
    combined_text = "\n\n".join(
        [chunk.page_content for chunk in chunks[:10]]
    )

    # 🔹 Summarization Prompt
    prompt = f"""
    You are an intelligent document summarizer.

    Summarize the uploaded document clearly.

    Focus on:
    - main topics
    - important insights
    - conclusions
    - key findings

    Document Content:
    {combined_text}

    Generate a clean structured summary.
    """

    summary = ask_llm(prompt)

    return {
        "summary": summary,
        "num_chunks": len(chunks)
    }