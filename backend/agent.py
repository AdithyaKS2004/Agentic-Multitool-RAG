# backend/agent.py

import ollama

from backend.tools.rag_tool import rag_tool
from backend.tools.web_tool import web_search
from backend.tools.summarizer_tool import summarizer_tool
import re
from backend.tools.comparison_tool import (
    comparison_tool
)

from backend.tools.calculator_tool import calculator_tool
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

    query_lower = query.lower().strip()

# ======================================
# 🔹 CALCULATOR
# ======================================

    math_keywords = [
        "sqrt",
        "pow",
        "calculate",
        "square root"
    ]

    if any(word in query_lower for word in math_keywords):

        return "CALCULATOR"

    math_pattern = r'^[0-9a-zA-Z\\s\\+\\-\\*\\/\\(\\)\\.,]+$'

    if re.match(math_pattern, query_lower):

        # prevent normal sentences
        if any(char.isdigit() for char in query_lower):

            return "CALCULATOR"

    # ======================================
    # 🔹 WEB
    # ======================================

    web_keywords = [
        "latest",
        "news",
        "today",
        "recent",
        "current",
        "update"
    ]

    if any(word in query_lower for word in web_keywords):

        return "WEB"

    # ======================================
    # 🔹 SUMMARIZER
    # ======================================

    summarizer_keywords = [
        "summarize",
        "summary",
        "overview",
        "brief"
    ]

    if any(word in query_lower for word in summarizer_keywords):

        return "SUMMARIZER"

    # ======================================
    # 🔹 COMPARISON
    # ======================================

    comparison_keywords = [
        "compare",
        "difference",
        "differences",
        "similarities",
        "similar",
        "contrast"
    ]

    if any(word in query_lower for word in comparison_keywords):

        return "COMPARISON"
    # ======================================
    # 🔹 DEFAULT → RAG
    # ======================================

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
            You are a document-grounded AI assistant.

            Your task:
            Rewrite the retrieved context into a clean,
            well-structured answer.

            IMPORTANT RULES:
            - Use ONLY the retrieved context
            - DO NOT add outside knowledge
            - DO NOT invent information
            - DO NOT expand beyond the context
            - DO NOT hallucinate
            - Keep the answer concise and accurate
            - Preserve factual correctness

            User Question:
            {query}

            Retrieved Context:
            {retrieved_answer}

            Generate a clean answer using ONLY the context.
            """

            return ask_llm(prompt)
        
    # ======================================
    # 🔹 WEB-GROUNDED GENERATION  ← ADD THIS
    # ======================================

    if tool_used == "WEB":                                      # ← ADD
        web_results = ""                                        # ← ADD
                                                                # ← ADD
        if isinstance(tool_output, dict):                       # ← ADD
            results = tool_output.get("results", [])            # ← ADD
            for i, r in enumerate(results, 1):                  # ← ADD
                web_results += (                                # ← ADD
                    f"[{i}] {r.get('title', '')}\n"            # ← ADD
                    f"{r.get('body', '')}\n"                   # ← ADD
                    f"Source: {r.get('link', '')}\n\n"         # ← ADD
                )                                               # ← ADD
                                                                # ← ADD
        prompt = f"""                                           
        You are a highly accurate AI assistant.
        Answer the question ONLY using the web search results below.
        DO NOT use your training knowledge for factual claims.
        DO NOT say 'as of my last update' — you have live results.
        If results are insufficient, say so clearly.

        User Question: {query}

        Web Search Results:
        {web_results}
        """                                                     # ← ADD
        return ask_llm(prompt)                                  # ← ADD
    
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

        elif tool == "CALCULATOR":

            return calculator_tool(query)
        
        elif tool == "COMPARISON":
            
            return comparison_tool(query)

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

    # ======================================
    # 🔹 RAG FALLBACK TO WEB
    # ======================================

    if tool == "RAG":

        # ensure tool output is dictionary
        if isinstance(tool_output, dict):

            # check relevance flag
            relevant = tool_output.get(
                "relevant",
                True
            )

            # if uploaded docs are not relevant
            if not relevant:

                print(
                    "RAG not relevant → switching to WEB"
                )

                # switch tool
                tool = "WEB"

                # execute web search instead
                tool_output = execute_tool(
                    tool,
                    query
                )
    # ==========================
    # STEP 3 → SIMPLE CONFIDENCE
    # ==========================
    quality = "GOOD"

    if tool_output is None:

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