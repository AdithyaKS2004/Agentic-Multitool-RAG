# frontend/streamlit_app.py

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

if "filenames" not in st.session_state:
    st.session_state.filenames = []


# ======================================
# 🔹 TITLE
# ======================================

st.title("📄 Agentic Multi-Tool RAG System")

st.markdown(
    """
    Upload multiple PDF documents, generate summaries,
    ask questions, and compare documents using AI.
    """
)


# ======================================
# 🔹 FILE UPLOADER
# ======================================

uploaded_file = st.file_uploader(
    "Upload PDF Documents",
    type=["pdf"],
    accept_multiple_files=True
)


# ======================================
# 🔹 DISPLAY UPLOADED FILES
# ======================================

if uploaded_file:

    st.subheader("📂 Uploaded Documents")

    for file in uploaded_file:
        st.write(f"• {file.name}")


# ======================================
# 🔹 DOCUMENT PROCESSING
# ======================================

if uploaded_file:

    col1, col2 = st.columns(2)

    # ==========================
    # 🔹 GENERATE SUMMARY
    # ==========================

    with col1:

        if st.button("Generate Summary"):

            with st.spinner("Generating summary..."):

                try:

                    files = []

                    for file in uploaded_file:

                        files.append(
                            (
                                "files",
                                (
                                    file.name,
                                    file.getvalue(),
                                    "application/pdf"
                                )
                            )
                        )

                    response = requests.post(
                        f"{BACKEND_URL}/upload-summary",
                        files=files
                    )

                    result = response.json()

                    st.session_state.uploaded = True
                    st.session_state.summary = result.get(
                        "summary",
                        "No summary generated"
                    )

                    st.session_state.filenames = [
                        file.name for file in uploaded_file
                    ]

                    st.success("Summary generated successfully")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # ==========================
    # 🔹 PROCESS FOR QA
    # ==========================

    with col2:

        if st.button("Enable Document QA"):

            with st.spinner(
                "Preparing documents for question answering..."
            ):

                try:

                    files = []

                    for file in uploaded_file:

                        files.append(
                            (
                                "files",
                                (
                                    file.name,
                                    file.getvalue(),
                                    "application/pdf"
                                )
                            )
                        )

                    response = requests.post(
                        f"{BACKEND_URL}/upload-document",
                        files=files
                    )

                    result = response.json()

                    if result.get("status") == "success":

                        st.success(
                            "Documents ready for question answering"
                        )

                        st.session_state.uploaded = True

                    else:
                        st.error("Failed to process documents")

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

st.subheader("💬 Ask Questions About Uploaded Documents")

query = st.text_input(
    "Enter your question"
)


# ======================================
# 🔹 ASK QUESTION
# ======================================

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

                # ==========================
                # 🔹 ANSWER
                # ==========================

                st.subheader("🤖 Answer")

                st.write(
                    result.get(
                        "answer",
                        "No answer generated"
                    )
                )

                # ==========================
                # 🔹 TOOL USED
                # ==========================

                st.info(
                    f"Tool Used: "
                    f"{result.get('tool_used', 'RAG')}"
                )

                # ==========================
                # 🔹 ANSWER QUALITY
                # ==========================

                if "answer_quality" in result:

                    st.success(
                        f"Answer Quality: "
                        f"{result['answer_quality']}"
                    )

                # ==========================
                # 🔹 SOURCES
                # ==========================

                if "sources" in result:

                    st.subheader("📚 Sources")

                    sources = result["sources"]

                    shown = set()

                    for source in sources:

                        if isinstance(source, dict):

                            src = source.get("source", "Unknown")
                            page = source.get("page", "N/A")

                            key = f"{src}-{page}"

                            if key not in shown:

                                st.write(
                                    f"• {src} "
                                    f"(Page {page})"
                                )

                                shown.add(key)

                # ==========================
                # 🔹 RAW TOOL OUTPUT
                # ==========================

                with st.expander("View Raw Tool Output"):

                    st.json(result)

            except Exception as e:

                st.error(f"Error: {str(e)}")