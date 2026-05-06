import streamlit as st
from pathlib import Path
import sys
import json
import tempfile
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ui_theme import inject_theme
inject_theme()

from src.ingestion.pdf_loader import extract_text_from_pdf
from src.generation.llm_client import generate
from src.vectorstore.embedder import search_all_collections
from src.vectorstore.chroma_manager import get_collection_stats
import config

CHAT_HISTORY_FILE = Path("knowledge_base/feedback/global_chat_history.json")
CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_history():
    try:
        if CHAT_HISTORY_FILE.exists():
            return json.loads(CHAT_HISTORY_FILE.read_text(encoding="utf-8"))
    except: pass
    return []

def save_to_history(role, content):
    h = load_history()
    h.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
    CHAT_HISTORY_FILE.write_text(json.dumps(h, indent=2, ensure_ascii=False), encoding="utf-8")

st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")
st.title("💬 QA Chat Assistant")
st.markdown("Ask anything about your CR or QA process.")

if "messages"   not in st.session_state: st.session_state["messages"]   = []
if "cr_content" not in st.session_state: st.session_state["cr_content"] = ""

with st.sidebar:
    st.markdown("---")
    st.subheader("Chat Controls")
    if st.button("🆕 New Conversation", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
    st.markdown("---")
    h = load_history()
    st.markdown(f"**📜 {len(h)} messages saved globally**")

with st.expander("📎 Attach Context — CR / SRS / Any File", expanded=not bool(st.session_state["cr_content"])):
    tab1, tab2 = st.tabs(["📝 Paste Text", "📄 Upload PDF"])
    with tab1:
        pasted = st.text_area("Paste CR or SRS here", height=150,
            placeholder="Paste your CR description here...")
        if st.button("✅ Set as Context"):
            st.session_state["cr_content"] = pasted
            st.success("Context set!")
    with tab2:
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
                st.success(f"Extracted {len(pages)} pages")
                if st.button("✅ Use as Context"):
                    st.session_state["cr_content"] = pdf_text
                    st.success("Context set from PDF!")

if st.session_state["cr_content"]:
    st.caption(f"📎 Context: _{st.session_state['cr_content'][:100].replace(chr(10),' ')}..._")

st.subheader("💬 Conversation")

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask anything...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Search ALL collections
    all_results = search_all_collections(user_input, n_results_each=3)
    kb_text = ""
    for collection, results in all_results.items():
        for r in results:
            kb_text += f"\n[{collection}]\n{r['content']}\n---"

    # Add system stats
    stats = get_collection_stats()
    system_info = f"""
SYSTEM KNOWLEDGE BASE STATS:
- Change Requests: {stats.get(config.COLLECTION_CRS, 0)} chunks from {len(list(Path('knowledge_base/crs').glob('*.pdf')))} files
- SRS Documents: {stats.get(config.COLLECTION_SRS, 0)} chunks from {len(list(Path('knowledge_base/srs').glob('*.pdf')))} files
- Test Cases: {stats.get(config.COLLECTION_TEST_CASES, 0)} chunks from {len(list(Path('knowledge_base/test_cases').glob('*.pdf')))} files
- QA Issues: {stats.get(config.COLLECTION_QA_ISSUES, 0)} chunks from {len(list(Path('knowledge_base/qa_issues').glob('*.pdf')))} files
"""
    kb_text = system_info + "\n\n" + kb_text

    cr_ctx = st.session_state["cr_content"] or "Not provided"
    history_text = ""
    for m in st.session_state["messages"][-6:]:
        role = "User" if m["role"] == "user" else "Assistant"
        history_text += f"{role}: {m['content']}\n"

    prompt = f"""You are a QA Assistant. Answer the question using the knowledge base content below.

KNOWLEDGE BASE CONTENT FROM UPLOADED DOCUMENTS:
{kb_text if kb_text else "No results found"}

CR CONTEXT PROVIDED BY USER:
{cr_ctx}

CONVERSATION HISTORY:
{history_text}

USER QUESTION: {user_input}

Answer based on the knowledge base content above. Be specific and detailed."""

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate(prompt=prompt, system_prompt="You are a helpful QA assistant.", temperature=0.3)
        st.markdown(response)

    st.session_state["messages"].append({"role": "assistant", "content": response})
    save_to_history("user", user_input)
    save_to_history("assistant", response)
    st.rerun()