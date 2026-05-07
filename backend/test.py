#from backend.rag_pipeline import load_pdfs
#from backend.rag_pipeline import split_documents 
from backend.agent import agent

#from backend.rag_pipeline import load_pdfs, split_documents, create_vectorstore, save_vectorstore,create_bm25_index

'''docs = load_pdfs(["data/pdfs/sample.pdf"])
print(len(docs))
print(docs[0].page_content[:200])

chunks = split_documents(docs)
print(len(chunks))
print(chunks[0].page_content)


#docs = load_pdfs(["data/pdfs/sample.pdf"])

vectorstore = create_vectorstore(chunks)
save_vectorstore(vectorstore)

#docs = load_pdfs([...])
chunks = split_documents(docs)

#vectorstore = create_vectorstore(chunks)#
bm25, texts = create_bm25_index(chunks)
'''

#print(agent("What is ovarian cancer?"))      # → RAG
#print(agent("latest news on ovarian cancer")) # → WEB


while True:
    query = input("\nAsk: ")

    if query.lower() == "exit":
        break

    response = agent(query)

    print("\n====================")
    print("TOOL USED:", response["tool_used"])
    print("QUALITY:", response["answer_quality"])
    print("ANSWER:\n")
    print(response["answer"])
    print("====================")

