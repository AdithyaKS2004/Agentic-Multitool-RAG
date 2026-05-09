import os

from langchain_community.document_loaders import PyPDFLoader


def load_pdfs(pdf_folder):

    documents = []

    for file in os.listdir(pdf_folder):

        if file.endswith(".pdf"):

            path = os.path.join(pdf_folder, file)

            print(f"Loading: {file}")

            loader = PyPDFLoader(path)

            docs = loader.load()

            # 🔹 add source metadata
            for doc in docs:
                doc.metadata["source"] = file

            documents.extend(docs)

    return documents