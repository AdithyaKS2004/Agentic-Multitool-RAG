import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data")
VECTORSTORE_PATH = os.path.join(BASE_DIR, "vectorstore")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"