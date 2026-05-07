# backend/rag_pipeline.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from rank_bm25 import BM25Okapi

# ================================
# 🔹 CONFIG
# ================================

VECTORSTORE_PATH = "vectorstore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ================================
# 🔹 EMBEDDINGS (Single Source of Truth)
# ================================

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# ================================
# 🔹 VECTORSTORE (LOAD ONLY — NO CREATION HERE)
# ================================

def load_vectorstore(path=VECTORSTORE_PATH):
    embeddings = get_embeddings()

    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )


# ================================
# 🔹 RETRIEVAL (FAISS)
# ================================

def retrieve_docs(vectorstore, query, k=5):
    return vectorstore.similarity_search(query, k=k)


# ================================
# 🔹 BM25 (KEYWORD SEARCH)
# ================================

def create_bm25_index(docs):
    texts = [doc.page_content for doc in docs]
    tokenized = [text.split() for text in texts]

    bm25 = BM25Okapi(tokenized)

    return bm25, texts


# ================================
# 🔹 HYBRID RETRIEVAL
# ================================

def hybrid_retrieve(query, vectorstore, bm25, texts, k=5):
    # 🔹 Semantic search (FAISS)
    semantic_docs = vectorstore.similarity_search(query, k=k)

    semantic_texts = [doc.page_content for doc in semantic_docs]

    # 🔹 Keyword search (BM25)
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)

    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    keyword_texts = [texts[i] for i in top_indices]

    # 🔹 Combine + deduplicate
    combined = list(dict.fromkeys(semantic_texts + keyword_texts))

    return combined[:k]


# ================================
# 🔹 ANSWER GENERATION (IMPROVED)
# ================================

def generate_answer(query, docs):
    """
    docs: list of strings (NOT Document objects)
    """

    if not docs:
        return "No relevant information found."

    context = " ".join(docs)

    # simple relevance filtering
    sentences = context.split(". ")

    query_words = set(query.lower().split())

    scored = []
    for sentence in sentences:
        score = sum(1 for word in query_words if word in sentence.lower())
        scored.append((score, sentence))

    # sort by relevance
    scored.sort(reverse=True, key=lambda x: x[0])

    top_sentences = [s for _, s in scored[:3]]

    return ". ".join(top_sentences)


# ================================
# 🔹 LOAD EVERYTHING (ENTRY POINT)
# ================================

def load_all():
    # 🔹 Load vectorstore (from processing)
    vectorstore = load_vectorstore()

    # 🔹 Get documents from vectorstore (for BM25)
    docs = vectorstore.similarity_search("", k=1000)  # get all-ish docs

    # fallback if empty
    if not docs:
        raise ValueError("Vectorstore is empty. Run processing first.")

    bm25, texts = create_bm25_index(docs)

    return vectorstore, bm25, texts