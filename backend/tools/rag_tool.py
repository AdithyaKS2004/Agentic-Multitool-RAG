# backend/tools/rag_tool.py
'''
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
        k=4
    )

    # 🔹 Generate answer
    answer = generate_answer(query, docs)
# ======================================
# 🔹 RELEVANCE CHECK
# ======================================

    top_score = None

    if docs and isinstance(docs[0], dict):

        top_score = docs[0].get("score")

# weak retrieval
    if top_score is not None and top_score > 1.0:

        return {
            "tool": "RAG",
            "query": query,
            "answer": answer,
            "sources": docs[:3],
            "relevant": True
        }
'''



# backend/tools/rag_tool.py

from backend.rag_pipeline import (
    load_all,
    hybrid_retrieve,
    generate_answer
)

from backend.temp_rag import (
    query_uploaded_document
)


# ======================================
# 🔹 LOAD GLOBAL VECTORSTORE
# ======================================

vectorstore, bm25, texts = load_all()


# ======================================
# 🔹 MAIN RAG TOOL
# ======================================

def rag_tool(query: str):

    try:

        # ======================================
        # 🔹 CHECK UPLOADED DOCUMENTS FIRST
        # ======================================

        uploaded_docs = query_uploaded_document(
            query=query,
            k=4
        )

        # uploaded document retrieval exists
        if uploaded_docs:

            # relevance check
            best_score = uploaded_docs[0].get(
                "score",
                999
            )

            # weak retrieval
            if best_score <= 1.0:

                answer = generate_answer(
                    query,
                    uploaded_docs
                )

                return {
                    "tool": "UPLOADED_DOCUMENT_RAG",
                    "query": query,
                    "answer": answer,
                    "sources": uploaded_docs[:3],
                    "relevant": True
                }

        # ======================================
        # 🔹 FALLBACK TO MAIN VECTORSTORE
        # ======================================

        docs = hybrid_retrieve(
            query=query,
            vectorstore=vectorstore,
            bm25=bm25,
            texts=texts,
            k=4
        )

        # ======================================
        # 🔹 NO RESULTS
        # ======================================

        if not docs:

            return {
                "tool": "RAG",
                "query": query,
                "answer": "",
                "sources": [],
                "relevant": False
            }

        # ======================================
        # 🔹 RELEVANCE CHECK
        # ======================================

        top_score = docs[0].get(
            "score",
            999
        )

        # weak retrieval
        if top_score > 1.0:

            return {
                "tool": "RAG",
                "query": query,
                "answer": "",
                "sources": [],
                "relevant": False
            }

        # ======================================
        # 🔹 GENERATE ANSWER
        # ======================================

        answer = generate_answer(
            query,
            docs
        )

        return {
            "tool": "RAG",
            "query": query,
            "answer": answer,
            "sources": docs[:3],
            "relevant": True
        }

    except Exception as e:

        return {
            "tool": "RAG",
            "query": query,
            "answer": "",
            "sources": [],
            "relevant": False,
            "error": str(e)
        }

