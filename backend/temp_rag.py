from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


VECTORSTORE = None


def process_uploaded_document(pdf_path):

    global VECTORSTORE

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    VECTORSTORE = FAISS.from_documents(
        chunks,
        embeddings
    )


def query_uploaded_document(query, k=3):

    global VECTORSTORE

    if VECTORSTORE is None:
        return []

    docs = VECTORSTORE.similarity_search(query, k=k)

    return [doc.page_content for doc in docs]