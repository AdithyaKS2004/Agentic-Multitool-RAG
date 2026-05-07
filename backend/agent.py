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

    planner_prompt = f"""
    You are an intelligent AI planner.

    Decide which tool is best for the user query.

    Available tools:

    1. RAG
    - Use for:
      document-based questions,
      explanations,
      domain knowledge,
      research-related questions

    2. WEB
    - Use for:
      latest news,
      current events,
      real-time information,
      recent updates

    3. SUMMARIZER
    - Use for:
      summarizing long content,
      summarizing topics,
      concise overviews

    User Query:
    {query}

    IMPORTANT:
    Reply ONLY with one word:
    RAG
    WEB
    or
    SUMMARIZER
    """

    try:
        decision = ask_llm(planner_prompt).strip().upper()

        if "WEB" in decision:
            return "WEB"

        elif "SUMMARIZER" in decision:
            return "SUMMARIZER"

        return "RAG"

    except Exception:
        return "RAG"


# ======================================
# 🔹 REFLECTOR
# ======================================

def reflect_answer(query, tool_output):

    reflection_prompt = f"""
    You are an AI evaluator.

    Evaluate the quality of the tool output.

    User Query:
    {query}

    Tool Output:
    {tool_output}

    Determine whether the output is:
    GOOD
    or
    BAD

    Reply ONLY with:
    GOOD
    or
    BAD
    """

    try:
        reflection = ask_llm(reflection_prompt).strip().upper()

        if "BAD" in reflection:
            return "BAD"

        return "GOOD"

    except Exception:
        return "UNKNOWN"


# ======================================
# 🔹 FINAL ANSWER GENERATOR
# ======================================

def generate_final_answer(query, tool_used, tool_output):

    memory = get_memory()

    final_prompt = f"""
    You are an intelligent AI assistant.

    Use the provided tool output to answer the user query.

    Conversation Memory:
    {memory}

    User Query:
    {query}

    Tool Used:
    {tool_used}

    Tool Output:
    {tool_output}

    Instructions:
    - Give a clear answer
    - Be concise but informative
    - Structure the response properly
    - If information is limited, say so honestly
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

    # default quality
    quality = "UNKNOWN"

    # ==========================
    # STEP 1 → PLAN
    # ==========================
    tool = choose_tool(query)

    # ==========================
    # STEP 2 → EXECUTE TOOL
    # ==========================
    tool_output = execute_tool(tool, query)

    # ==========================
    # STEP 3 → REFLECT
    # ==========================
    quality = reflect_answer(query, tool_output)
   
    # ==========================
    # STEP 4 → FALLBACK
    # ==========================
    if quality == "BAD":

        # fallback strategy
        if tool == "WEB":

            tool = "RAG"
            tool_output = execute_tool(tool, query)

        elif tool == "RAG":

            tool = "SUMMARIZER"
            tool_output = execute_tool(tool, query)

        else:

            tool = "RAG"
            tool_output = execute_tool(tool, query)
    
    # ==========================
    # STEP 5 → FINAL RESPONSE
    # ==========================
    answer = generate_final_answer(
        query,
        tool,
        tool_output
    )

    # ==========================
    # STEP 6 → SAVE MEMORY
    # ==========================
    save_memory(query, answer)

    # ==========================
    # STEP 7 → DEBUG LOG
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
    # STEP 8 → RETURN
    # ==========================
    return response_data