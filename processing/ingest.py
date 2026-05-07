from processing.loader import load_pdfs
from processing.chunking import split_documents
from processing.embeddings import get_embedding_model
from processing.vectorstore import create_vectorstore
from processing.config import DATA_PATH, VECTORSTORE_PATH

def run_ingestion():
    print("🔹 Loading PDFs...")
    documents = load_pdfs(DATA_PATH)
    print(f"Loaded documents: {len(documents)}")

    if len(documents) == 0:
        raise ValueError("❌ No documents loaded")

    print("🔹 Splitting documents...")
    chunks = split_documents(documents)
    print(f"Chunks created: {len(chunks)}")

    if len(chunks) == 0:
        raise ValueError("❌ No chunks created")

    print("🔹 Loading embeddings...")
    embedding_model = get_embedding_model()

    print("🔹 Creating vectorstore...")
    create_vectorstore(chunks, embedding_model, VECTORSTORE_PATH)

    print("✅ Done!")


if __name__ == "__main__":
    run_ingestion()