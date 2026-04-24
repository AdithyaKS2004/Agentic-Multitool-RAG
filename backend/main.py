from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Request format
class QueryRequest(BaseModel):
    query: str
    tool: str

# Response format
@app.post("/query")
def handle_query(request: QueryRequest):
    
    query = request.query
    tool = request.tool

    # TEMP response (we’ll replace later)
    return {
        "answer": f"Received query: {query} using tool: {tool}",
        "sources": []
    }