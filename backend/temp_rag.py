# backend/temp_rag.py

import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


VECTORSTORE = None


# ======================================
# 🔹 PROCESS MULTIPLE DOCUMENTS
# ======================================

def process_uploaded_document(folder_path):

    global VECTORSTORE

    all_docs = []

    # load all PDFs
    for file in os.listdir(folder_path):

        if file.endswith(".pdf"):

            pdf_path = os.path.join(folder_path, file)

            loader = PyPDFLoader(pdf_path)

            docs = loader.load()

            # source metadata
            for doc in docs:
                doc.metadata["source"] = file

            all_docs.extend(docs)

    # split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(all_docs)

    # embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # vectorstore
    VECTORSTORE = FAISS.from_documents(
        chunks,
        embeddings
    )


# ======================================
# 🔹 QUERY
# ======================================

def query_uploaded_document(query, k=4):

    global VECTORSTORE

    if VECTORSTORE is None:
        return []

    docs = VECTORSTORE.similarity_search_with_score(
        query,
        k=k
    )

    results = []

    for doc, score in docs:

        if score < 1.2:

            results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source"),
                "page": int(doc.metadata.get("page", 0)),
                "score": float(score)
            })

    return results