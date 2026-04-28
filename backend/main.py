from fastapi import FastAPI
from pydantic import BaseModel
from backend.rag_pipeline import load_vectorstore, retrieve_docs, generate_answer,hybrid_retrieve,load_all
from backend.tools.calculator_tool import calculate
from backend.tools.web_tool import web_search, format_web_results

vectorstore, bm25, texts = load_all()


app = FastAPI()

# ✅ Load once at startup
#vectorstore = load_vectorstore()


# ✅ Request schema
class QueryRequest(BaseModel):
    query: str
    tool: str = "rag"   # default (optional but useful)

'''
# ✅ Route
@app.post("/query")
def handle_query(request: QueryRequest):
    
    query = request.query
    tool = request.tool

    # ✅ RAG flow
    if tool == "rag":
        docs = retrieve_docs(vectorstore, query)

        if not docs:
            return {
                "answer": "No relevant documents found",
                "sources": []
            }

        context = "\n\n".join([d.page_content for d in docs])

        return {
            "answer": context[:500],  # temporary (will replace with LLM later)
            "sources": ["PDF"]
        }

    # ✅ fallback
    return {
        "answer": f"Tool '{tool}' not implemented yet",
        "sources": []
    }'''







@app.post("/query")
def handle_query(request: QueryRequest):
    
    query = request.query
    tool = request.tool

    if tool == "calculator":
        result = calculate(query)
        return {
            "answer": result,
            "sources": ["Calculator"]
        }


    if tool == "rag":
        docs = hybrid_retrieve(query, vectorstore, bm25, texts)
        answer = generate_answer(query, docs)

        return {
            "answer": answer,
            "sources": ["Hybrid RAG"]
        }
    
    if tool == "web":
        results = web_search(query)
        answer = format_web_results(results)

        return {
            "answer": answer,
            "sources": [r["link"] for r in results if r["link"]]
        }

    return {
        "answer": "Tool not implemented yet",
        "sources": []
    }

