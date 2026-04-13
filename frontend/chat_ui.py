"""Streamlit chat interface for the financial document chatbot.

Connects to the FastAPI backend to upload PDFs and ask questions
in a conversational UI with message history.
"""

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Financial Doc Chatbot", layout="wide")
st.title("📊 Financial Document Chatbot")
st.caption("Upload financial PDFs and ask questions — answers are grounded in your documents.")

# ── Sidebar: PDF upload ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📄 Upload Documents")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("Uploading and processing…"):
            try:
                resp = requests.post(
                    f"{API_URL}/upload/",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                    timeout=120,
                )
                if resp.status_code == 200:
                    st.success(resp.json().get("status", "Done"))
                else:
                    st.error(f"Upload failed: {resp.text}")
            except requests.ConnectionError:
                st.error("Cannot connect to the backend. Is the API server running?")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

# ── Chat state ───────────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask a question about your documents…")

if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Query backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                resp = requests.get(
                    f"{API_URL}/query/",
                    params={"q": prompt},
                    timeout=60,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("answer", "No answer found.")
                    sources = data.get("sources", [])

                    # Format response
                    reply = answer
                    if sources:
                        source_list = "\n".join(f"- `{s}`" for s in sources)
                        reply += f"\n\n**Sources:**\n{source_list}"

                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    error_text = f"⚠️ API error: {resp.text}"
                    st.error(error_text)
                    st.session_state.messages.append({"role": "assistant", "content": error_text})

            except requests.ConnectionError:
                err = "⚠️ Cannot connect to the backend. Is the API server running?"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
            except Exception as exc:
                err = f"⚠️ Unexpected error: {exc}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
