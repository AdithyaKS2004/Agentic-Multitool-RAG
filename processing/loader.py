from langchain_community.document_loaders import PyPDFLoader
import os

def load_pdfs(data_path):
    documents = []

    for root, _, files in os.walk(data_path):   # 🔥 recursive
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                print(f"Loading: {file_path}")

                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())

    return documents