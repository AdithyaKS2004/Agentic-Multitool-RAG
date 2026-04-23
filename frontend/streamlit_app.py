import streamlit as st
import requests

st.set_page_config(page_title="Agentic RAG System", layout="wide")

st.title("🤖 Agentic Multi-Tool RAG System")

# Sidebar for file upload
st.sidebar.header("Upload Documents")
uploaded_files = st.sidebar.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

# Main chat input
st.subheader("Ask a Question")

user_query = st.text_input("Enter your question:")

if st.button("Submit"):
    if user_query:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"query": user_query}
                )

                if response.status_code == 200:
                    result = response.json()

                    st.subheader("Answer")
                    st.write(result.get("answer", "No answer found"))

                    st.subheader("Sources")
                    for src in result.get("sources", []):
                        st.write(f"- {src}")

                else:
                    st.error("Backend error")

            except Exception as e:
                st.error("Backend not running yet")