import streamlit as st
import requests


# ======================================
# 🔹 PAGE CONFIG
# ======================================

st.set_page_config(
    page_title="Agentic Multi-Tool RAG",
    layout="wide"
)


# ======================================
# 🔹 BACKEND URL
# ======================================

BACKEND_URL = "http://127.0.0.1:8000"


# ======================================
# 🔹 SESSION STATE
# ======================================

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "filename" not in st.session_state:
    st.session_state.filename = ""


# ======================================
# 🔹 TITLE
# ======================================

st.title("📄 Agentic Multi-Tool RAG System")
st.markdown("Upload documents, generate summaries, and ask questions using AI.")


# ======================================
# 🔹 FILE UPLOADER
# ======================================

uploaded_file = st.file_uploader(
    "Upload PDF Document",
    type=["pdf"]
)


# ======================================
# 🔹 DOCUMENT PROCESSING
# ======================================

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    col1, col2 = st.columns(2)

    # ==========================
    # 🔹 GENERATE SUMMARY
    # ==========================

    with col1:

        if st.button("Generate Summary"):

            with st.spinner("Generating summary..."):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }

                    response = requests.post(
                        f"{BACKEND_URL}/upload-summary",
                        files=files
                    )

                    result = response.json()

                    st.session_state.uploaded = True
                    st.session_state.summary = result["summary"]
                    st.session_state.filename = uploaded_file.name

                except Exception as e:
                    st.error(f"Error: {str(e)}")


    # ==========================
    # 🔹 PROCESS FOR QA
    # ==========================

    with col2:

        if st.button("Enable Document QA"):

            with st.spinner("Preparing document for question answering..."):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }

                    response = requests.post(
                        f"{BACKEND_URL}/upload-document",
                        files=files
                    )

                    result = response.json()

                    if result.get("status") == "success":
                        st.success("Document ready for Q&A")
                        st.session_state.uploaded = True

                    else:
                        st.error("Failed to process document")

                except Exception as e:
                    st.error(f"Error: {str(e)}")


# ======================================
# 🔹 DISPLAY SUMMARY
# ======================================

if st.session_state.summary:

    st.subheader("📌 Document Summary")

    with st.expander("View Summary", expanded=True):
        st.write(st.session_state.summary)


# ======================================
# 🔹 QUESTION ANSWERING
# ======================================

st.divider()

st.subheader("💬 Ask Questions About Uploaded Document")

query = st.text_input(
    "Enter your question"
)


if st.button("Ask Question"):

    if not query:
        st.warning("Please enter a question")

    else:

        with st.spinner("Generating answer..."):

            try:

                payload = {
                    "query": query
                }

                response = requests.post(
                    f"{BACKEND_URL}/ask-document",
                    json=payload
                )

                result = response.json()

                st.subheader("🤖 Answer")
                st.write(result.get("answer", "No answer generated"))

                st.info(f"Tool Used: {result.get('tool_used', 'RAG')}")

                if "answer_quality" in result:
                    st.success(
                        f"Answer Quality: {result['answer_quality']}"
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")