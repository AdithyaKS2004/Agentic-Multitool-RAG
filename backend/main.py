from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from backend.rag_pipeline import load_vectorstore, retrieve_docs, generate_answer,hybrid_retrieve,load_all
from backend.tools.calculator_tool import calculator_tool
from backend.tools.web_tool import web_search, format_web_results
from backend.agent import agent
import shutil
import os 
from backend.tools.realtime_summarizer import summarize_uploaded_document
from backend.temp_rag import process_uploaded_document

vectorstore, bm25, texts = load_all()
#docs = hybrid_retrieve(query, vectorstore, bm25, texts)
#answer = generate_answer(query, docs)
from backend.tools.realtime_summarizer import (
    summarize_uploaded_document
)

app = FastAPI()

# ✅ Load once at startup
#vectorstore = load_vectorstore()


# ✅ Request schema
class QueryRequest(BaseModel):
    query: str
    tool: str = "rag"   # default (optional but useful)



@app.get("/ask")
def ask(query: str):
    return agent(query)




@app.post("/query")
def handle_query(request: QueryRequest):
    
    query = request.query
    tool = request.tool

    if tool == "calculator":
        result = calculator_tool(query)
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

# ======================================
# 🔹 PDF UPLOAD + SUMMARY
# ======================================

@app.post("/upload-summary")
async def upload_summary(files: list[UploadFile] = File(...)):

    os.makedirs("uploads", exist_ok=True)

    uploaded_files = []

    combined_text = ""

    for file in files:

        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append(file.filename)

        # summarize each file
        result = summarize_uploaded_document(file_path)

        combined_text += f"\n\n=== {file.filename} ===\n"
        combined_text += result["summary"]

    return {
        "status": "success",
        "files_uploaded": uploaded_files,
        "summary": combined_text
    }
@app.post("/upload-document")
async def upload_document(files: list[UploadFile] = File(...)):

    os.makedirs("uploads", exist_ok=True)

    uploaded_files = []

    for file in files:

        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append(file.filename)

    # process ALL uploaded PDFs
    process_uploaded_document("uploads")

    return {
        "status": "success",
        "files_uploaded": uploaded_files
    }

@app.post("/ask-document")
async def ask_document(request: QueryRequest):

    response = agent(request.query)

    return response

