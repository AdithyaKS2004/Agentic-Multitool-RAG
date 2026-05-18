# backend/tools/calculator_tool.py

import math


def calculator_tool(query):

    try:

        # safe math environment
        allowed = {
            "__builtins__": {},
            "sqrt": math.sqrt,
            "pow": pow,
            "abs": abs,
            "round": round
        }

        result = eval(query, allowed)

        return {
            "tool": "CALCULATOR",
            "query": query,
            "answer": str(result)
        }

    except Exception as e:

        return {
            "tool": "CALCULATOR",
            "error": str(e)
        }