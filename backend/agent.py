# backend/agent.py

import ollama

from backend.tools.rag_tool import rag_tool
from backend.tools.web_tool import web_search
from backend.tools.summarizer_tool import summarizer_tool

from backend.config import OLLAMA_MODEL
from backend.memory import save_memory, get_memory


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
# 🔹 TOOL PLANNER
# ======================================

def choose_tool(query: str):

    # Faster rule-based routing
    # avoids unnecessary LLM latency

    query_lower = query.lower()

    # 🔹 web queries
    web_keywords = [
        "latest",
        "news",
        "today",
        "recent",
        "current",
        "update"
    ]

    # 🔹 summarizer queries
    summarizer_keywords = [
        "summarize",
        "summary",
        "overview",
        "brief"
    ]

    # 🔹 comparison queries
    comparison_keywords = [
        "compare",
        "difference",
        "similarities"
    ]

    # WEB
    if any(word in query_lower for word in web_keywords):
        return "WEB"

    # SUMMARIZER
    if any(word in query_lower for word in summarizer_keywords):
        return "SUMMARIZER"

    # RAG by default
    return "RAG"


# ======================================
# 🔹 FINAL ANSWER GENERATOR
# ======================================

def generate_final_answer(query, tool_used, tool_output):

    # ======================================
    # 🔹 RAG-GROUNDED GENERATION
    # ======================================

    if tool_used == "RAG":

        if isinstance(tool_output, dict):

            retrieved_answer = tool_output.get(
                "answer",
                ""
            )

            prompt = f"""
            You are a highly accurate AI assistant.

            Answer the question ONLY using
            the provided context.

            DO NOT add outside knowledge.
            DO NOT hallucinate.
            DO NOT invent information.

            User Question:
            {query}

            Retrieved Context:
            {retrieved_answer}

            Instructions:
            - give a detailed explanation
            - structure answer clearly
            - keep answer relevant
            - include key points
            - avoid repetition
            """

            return ask_llm(prompt)

    # ======================================
    # 🔹 OTHER TOOLS
    # ======================================

    memory = get_memory()

    final_prompt = f"""
    You are an intelligent AI assistant.

    Conversation Memory:
    {memory}

    User Query:
    {query}

    Tool Used:
    {tool_used}

    Tool Output:
    {tool_output}

    Generate a concise and accurate answer.
    """

    try:

        return ask_llm(final_prompt)

    except Exception as e:

        return f"Error generating final answer: {str(e)}"


# ======================================
# 🔹 TOOL EXECUTOR
# ======================================

def execute_tool(tool, query):

    try:

        if tool == "WEB":

            return web_search(query)

        elif tool == "SUMMARIZER":

            return summarizer_tool(query)

        else:

            return rag_tool(query)

    except Exception as e:

        return {
            "tool": tool,
            "error": str(e)
        }


# ======================================
# 🔹 MAIN AGENT PIPELINE
# ======================================

def agent(query: str):

    # ==========================
    # STEP 1 → PLAN
    # ==========================
    tool = choose_tool(query)

    # ==========================
    # STEP 2 → EXECUTE TOOL
    # ==========================
    tool_output = execute_tool(tool, query)

    # ==========================
    # STEP 3 → SIMPLE CONFIDENCE
    # ==========================
    quality = "GOOD"

    if not tool_output:

        quality = "LOW_CONFIDENCE"

    elif isinstance(tool_output, dict):

        if "error" in tool_output:

            quality = "ERROR"

    # ==========================
    # STEP 4 → FINAL RESPONSE
    # ==========================
    answer = generate_final_answer(
        query,
        tool,
        tool_output
    )

    # ==========================
    # STEP 5 → SAVE MEMORY
    # ==========================
    save_memory(query, answer)

    # ==========================
    # STEP 6 → DEBUG LOG
    # ==========================
    response_data = {
        "tool_used": tool,
        "answer_quality": quality,
        "tool_output": tool_output,
        "answer": answer
    }

    print("\nDEBUG RESPONSE:")
    print(response_data)

    # ==========================
    # STEP 7 → RETURN
    # ==========================
    return response_data