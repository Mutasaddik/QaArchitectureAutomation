import streamlit as st
from pathlib import Path
import sys
import json
import tempfile
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chat.chat_engine import chat_engine
from src.ingestion.pdf_loader import extract_text_from_pdf

CHAT_HISTORY_FILE = Path("knowledge_base/feedback/global_chat_history.json")
CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_global_history():
    try:
        if CHAT_HISTORY_FILE.exists():
            return json.loads(CHAT_HISTORY_FILE.read_text(encoding="utf-8"))
    except: pass
    return []

def append_to_global(role, content, cr_context=""):
    history = load_global_history()
    history.append({"role":role,"content":content,
        "cr_context":cr_context[:200],"timestamp":datetime.now().isoformat()})
    CHAT_HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")
st.title("💬 QA Chat Assistant")
st.markdown("Ask anything about your CR or QA process. All conversations are saved globally.")

if "chat_session_id" not in st.session_state:
    session = chat_engine.create_session()
    st.session_state["chat_session_id"] = session.session_id
    st.session_state["chat_cr_text"]    = ""

session = chat_engine.get_session(st.session_state["chat_session_id"])
if session is None:
    session = chat_engine.create_session()
    st.session_state["chat_session_id"] = session.session_id

with st.sidebar:
    st.markdown("---")
    st.subheader("Chat Controls")
    if st.button("🆕 New Conversation", use_container_width=True):
        new_s = chat_engine.create_session()
        st.session_state["chat_session_id"] = new_s.session_id
        st.session_state["chat_cr_text"]    = ""
        st.rerun()
    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        session.clear_history()
        st.rerun()
    st.markdown("---")
    global_history = load_global_history()
    st.markdown(f"**📜 {len(global_history)} messages saved globally**")
    if st.button("👁️ Toggle History", use_container_width=True):
        st.session_state["show_history"] = not st.session_state.get("show_history", False)

with st.expander("📎 Attach Context — CR / SRS / Any File", expanded=not bool(session.cr_text)):
    ctx_tab1, ctx_tab2 = st.tabs(["📝 Paste Text", "📄 Upload PDF"])
    with ctx_tab1:
        pasted = st.text_area("Paste CR, SRS, or any context",
            value=st.session_state.get("chat_cr_text",""), height=150,
            placeholder="Paste your CR or SRS here to give the AI context...")
        if st.button("✅ Set as Context"):
            session.cr_text = pasted
            st.session_state["chat_cr_text"] = pasted
            st.success("Context set!")
    with ctx_tab2:
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                tmp_path = Path(tmp.name)
            with st.spinner("Extracting..."):
                pages    = extract_text_from_pdf(tmp_path)
                pdf_text = "\n\n".join(p["text"] for p in pages)
                tmp_path.unlink()
            if pdf_text:
                st.success(f"Extracted {len(pages)} pages from {uploaded.name}")
                with st.expander("Preview"):
                    st.text(pdf_text[:400]+"...")
                if st.button("✅ Use This File as Context"):
                    session.cr_text = f"[File: {uploaded.name}]\n\n{pdf_text}"
                    st.session_state["chat_cr_text"] = session.cr_text
                    st.success("Context set from file!")

if session.cr_text:
    st.caption(f"📎 Context: _{session.cr_text[:120].replace(chr(10),' ')}..._")

if st.session_state.get("show_history"):
    st.markdown("---")
    st.subheader("📜 Global Chat History (last 30)")
    for msg in load_global_history()[-30:]:
        ts   = msg.get("timestamp","")[:16].replace("T"," ")
        role = "🧑 You" if msg["role"]=="user" else "🤖 Assistant"
        with st.expander(f"{role} — {ts}"):
            st.markdown(msg["content"])
    st.markdown("---")

st.subheader("💬 Current Conversation")
if not session.history:
    st.info("Start chatting below!\n\nExample:\n- What modules are impacted?\n- What are the high risk areas?\n- What test data do I need?\n- Are there known QA environment issues?")

for msg in session.history:
    with st.chat_message("user" if msg["role"]=="user" else "assistant"):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask anything about your CR, test strategy, QA process...")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(user_input, session, stream=False)
        st.markdown(response)
    append_to_global("user",      user_input, session.cr_text)
    append_to_global("assistant", response,   session.cr_text)
    st.rerun()