from langchain_community.vectorstores import FAISS
import os

def create_vectorstore(chunks, embedding_model, save_path):
    db = FAISS.from_documents(chunks, embedding_model)

    db.save_local(save_path)

    return db


def load_vectorstore(embedding_model, load_path):
    return FAISS.load_local(load_path, embedding_model)