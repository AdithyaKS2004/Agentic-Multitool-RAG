# backend/tools/rag_tool.py

from backend.rag_pipeline import load_all, hybrid_retrieve, generate_answer
from backend.temp_rag import query_uploaded_document
# Load once (important for performance)
vectorstore, bm25, texts = load_all()


def rag_tool(query: str):
    """
    Main RAG tool for answering document-based questions
    """
    uploaded_docs = query_uploaded_document(query)

    if uploaded_docs:
        answer = generate_answer(query, uploaded_docs)

        return {
            "tool": "UPLOADED_DOCUMENT_RAG",
            "query": query,
            "answer": answer,
            "sources": uploaded_docs[:3]
        }
    # 🔹 Hybrid retrieval
    docs = hybrid_retrieve(
        query=query,
        vectorstore=vectorstore,
        bm25=bm25,
        texts=texts,
        k=5
    )

    # 🔹 Generate answer
    answer = generate_answer(query, docs)

    return {
        "tool": "RAG",
        "query": query,
        "answer": answer,
        "sources": docs[:3]
    }