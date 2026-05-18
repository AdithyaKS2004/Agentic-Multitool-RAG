# frontend/streamlit_app.py

import streamlit as st
import requests


# ======================================
# 🔹 PAGE CONFIG
# ======================================

st.set_page_config(
    page_title="Agentic Multi-Tool RAG",
    page_icon="🤖",
    layout="wide"
)


# ======================================
# 🔹 HIDE STREAMLIT CLUTTER
# ======================================

st.markdown("""
<style>

/* Hide Streamlit menu */
#MainMenu {
    visibility: hidden;
}

/* Hide footer */
footer {
    visibility: hidden;
}

/* KEEP header visible so sidebar toggle works */
header {
    visibility: visible;
}

/* Cleaner spacing */
.block-container {
    padding-top: 2rem;
}

/* Chat styling */
.stChatMessage {
    border-radius: 12px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)

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

if "messages" not in st.session_state:
    st.session_state.messages = []


# ======================================
# 🔹 TITLE
# ======================================

st.markdown("""
# 🤖 Agentic Multi-Tool RAG System

### Intelligent Multi-Document Question Answering

Supports:
- Hybrid Retrieval
- Agentic AI Routing
- Multi-PDF QA
- Web Search
- Calculator Tool
- Cross-Document Comparison
""")


st.divider()


# ======================================
# 🔹 SIDEBAR
# ======================================

with st.sidebar:

    st.header("📂 Upload Documents")

    uploaded_file = st.file_uploader(
        "Upload PDF Documents",
        type=["pdf"],
        accept_multiple_files=True
    )

    st.divider()

    # ==========================
    # 🔹 DISPLAY FILES
    # ==========================

    if uploaded_file:

        st.subheader("Uploaded PDFs")

        for file in uploaded_file:
            st.write(f"• {file.name}")

    st.divider()

    # ==========================
    # 🔹 GENERATE SUMMARY
    # ==========================

    if uploaded_file:

        if st.button("📌 Generate Summary"):

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

                    st.session_state.summary = result.get(
                        "summary",
                        "No summary generated"
                    )

                    st.success(
                        "Summary generated successfully"
                    )

                except Exception as e:

                    st.error(f"Error: {str(e)}")

    # ==========================
    # 🔹 ENABLE QA
    # ==========================

    if uploaded_file:

        if st.button("🚀 Enable Document QA"):

            with st.spinner(
                "Preparing documents..."
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
                            "Documents ready for QA"
                        )

                        st.session_state.uploaded = True

                    else:

                        st.error(
                            "Failed to process documents"
                        )

                except Exception as e:

                    st.error(f"Error: {str(e)}")

    st.divider()

    # ==========================
    # 🔹 CLEAR CHAT
    # ==========================

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()


# ======================================
# 🔹 SUMMARY SECTION
# ======================================

if st.session_state.summary:

    with st.expander(
        "📌 View Document Summary",
        expanded=False
    ):

        st.write(
            st.session_state.summary
        )


# ======================================
# 🔹 CHAT HISTORY
# ======================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ======================================
# 🔹 CHAT INPUT
# ======================================

query = st.chat_input(
    "Ask questions about your documents..."
)
st.caption(
    "Example: Compare NLP and AI approaches"
)

# ======================================
# 🔹 HANDLE QUERY
# ======================================

if query:

    # ==========================
    # 🔹 USER MESSAGE
    # ==========================

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):

        st.markdown(query)

    # ==========================
    # 🔹 ASSISTANT RESPONSE
    # ==========================

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                payload = {
                    "query": query
                }

                response = requests.post(
                    f"{BACKEND_URL}/ask-document",
                    json=payload
                )

                result = response.json()

                answer = result.get(
                    "answer",
                    "No answer generated"
                )

                st.markdown(answer)

                # save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.divider()

                # ==========================
                # 🔹 TOOL INFO
                # ==========================

                col1, col2 = st.columns(2)

                with col1:

                    st.info(
                        f"🛠️ Tool Used: "
                        f"{result.get('tool_used', 'Unknown')}"
                    )

                with col2:

                    st.success(
                        f"✅ Quality: "
                        f"{result.get('answer_quality', 'GOOD')}"
                    )

                # ==========================
                # 🔹 SOURCES
                # ==========================

                if "tool_output" in result:

                    tool_output = result["tool_output"]

                    if isinstance(tool_output, dict):

                        sources = tool_output.get(
                            "sources",
                            []
                        )

                        if sources:

                            with st.expander(
                                "📚 Sources Used",
                                expanded=False
                            ):

                                shown = set()

                                for source in sources:

                                    if isinstance(
                                        source,
                                        dict
                                    ):

                                        src = source.get(
                                            "source",
                                            "Unknown"
                                        )

                                        page = source.get(
                                            "page",
                                            "N/A"
                                        )

                                        key = f"{src}-{page}"

                                        if key not in shown:

                                            st.write(
                                                f"• {src} "
                                                f"(Page {page})"
                                            )

                                            shown.add(key)

                # ==========================
                # 🔹 DEBUG OUTPUT
                # ==========================

                with st.expander(
                    "⚙️ Debug Info",
                    expanded=False
                ):

                    st.json(result)

            except Exception as e:

                st.error(f"Error: {str(e)}")