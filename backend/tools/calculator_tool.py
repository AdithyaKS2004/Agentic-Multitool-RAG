# backend/tools/calculator_tool.py

import math

def calculate(expression: str):
    try:
        # Safe eval (restricted)
        allowed_names = {
            "sqrt": math.sqrt,
            "pow": math.pow
        }

        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)

    except Exception:
        return "Invalid calculation"