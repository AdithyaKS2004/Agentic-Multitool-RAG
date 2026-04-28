# backend/rag_pipeline.py

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from rank_bm25 import BM25Okapi

'''from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS'''

def load_pdfs(pdf_paths):
    documents = []

    for path in pdf_paths:
        loader = PyPDFLoader(path)
        docs = loader.load()
        documents.extend(docs)

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)
    return chunks

    

'''def create_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    return embeddings



def create_vectorstore(chunks):
    embeddings = create_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


def save_vectorstore(vectorstore, path="vectorstore"):
    vectorstore.save_local(path)


def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )


def retrieve_docs(vectorstore, query):
    return vectorstore.similarity_search(query, k=3)'''




# ✅ Single source of truth for embeddings
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# ✅ Create vectorstore from chunks
def create_vectorstore(chunks):
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


# ✅ Save vectorstore locally
def save_vectorstore(vectorstore, path="vectorstore"):
    vectorstore.save_local(path)


# ✅ Load vectorstore safely
def load_vectorstore(path="vectorstore"):
    embeddings = get_embeddings()

    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )


# ✅ Retrieve top-k similar documents
def retrieve_docs(vectorstore, query, k=5):
    return vectorstore.similarity_search(query, k=k)

def generate_answer(query, docs):
    # Combine retrieved context
    context = " ".join(docs)

    # Basic filtering (optional improvement)
    sentences = context.split(". ")

    # Pick most relevant sentences
    relevant = [s for s in sentences if any(word in s.lower() for word in query.lower().split())]

    if not relevant:
        relevant = sentences[:3]

    answer = ". ".join(relevant[:3])

    return answer

def create_bm25_index(chunks):
    texts = [doc.page_content for doc in chunks]
    tokenized = [text.split() for text in texts]

    bm25 = BM25Okapi(tokenized)

    return bm25, texts

def hybrid_retrieve(query, vectorstore, bm25, texts, k=3):
    # 🔹 Semantic search
    semantic_docs = vectorstore.similarity_search(query, k=k)

    # 🔹 Keyword search
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)

    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    keyword_docs = [texts[i] for i in top_indices]

    # 🔹 Combine results
    combined = []

    for doc in semantic_docs:
        combined.append(doc.page_content)

    combined.extend(keyword_docs)

    return combined[:k]

def load_all():
    vectorstore = load_vectorstore()

    # load or recreate chunks
    docs = load_pdfs(["data/pdfs/sample.pdf"])
    chunks = split_documents(docs)

    bm25, texts = create_bm25_index(chunks)

    return vectorstore, bm25, texts




