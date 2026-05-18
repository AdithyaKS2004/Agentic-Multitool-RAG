
# backend/tools/comparison_tool.py

from backend.temp_rag import query_uploaded_document
import ollama

from backend.config import OLLAMA_MODEL


# ======================================
# 🔹 LLM HELPER
# ======================================

def ask_llm(prompt):

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
# 🔹 COMPARISON TOOL
# ======================================

def comparison_tool(query):

    try:

        docs = query_uploaded_document(
            query=query,
            k=6
        )

        if not docs:

            return {
                "tool": "COMPARISON",
                "answer": "No relevant documents found.",
                "sources": []
            }

        # ======================================
        # 🔹 GROUP BY SOURCE
        # ======================================

        grouped = {}

        for doc in docs:

            source = doc.get(
                "source",
                "Unknown"
            )

            content = doc.get(
                "content",
                ""
            )

            if source not in grouped:
                grouped[source] = []

            grouped[source].append(content)
        
        # ======================================
        # 🔹 VERIFY MULTIPLE DOCUMENTS
        # ======================================

        if len(grouped.keys()) < 2:

            return {
                "tool": "COMPARISON",
                "query": query,
                "answer": (
                    "At least two different documents "
                    "are required for comparison."
                ),
                "sources": list(grouped.keys())
            }
        # ======================================
        # 🔹 BUILD CONTEXT
        # ======================================

        comparison_context = ""

        for source, contents in grouped.items():

            comparison_context += (
                f"\n\nDOCUMENT: {source}\n"
            )

            comparison_context += (
                "\n".join(contents[:2])
            )

        # ======================================
        # 🔹 STRICT COMPARISON PROMPT
        # ======================================

        prompt = f"""
        You are a document-grounded AI assistant.

        Compare the uploaded documents
        using ONLY the provided context.

        IMPORTANT RULES:
        - Do NOT hallucinate
        - Do NOT add outside knowledge
        - Compare similarities and differences
        - Mention document names where relevant
        - Keep answer structured and clear

        User Query:
        {query}

        Document Context:
        {comparison_context}

        Generate a comparison answer.
        """

        answer = ask_llm(prompt)

        return {
            "tool": "COMPARISON",
            "query": query,
            "answer": answer,
            "sources": list(grouped.keys())
        }

    except Exception as e:

        return {
            "tool": "COMPARISON",
            "answer": "",
            "sources": [],
            "error": str(e)
        }

