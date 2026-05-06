# ui/pages/4_📚_Knowledge_Manager.py
import streamlit as st
from pathlib import Path
import sys
import shutil
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ingestion.ingest_pipeline import ingest_single_file, get_ingestion_stats
from src.vectorstore.chroma_manager import get_collection_stats, delete_collection
import config

st.set_page_config(page_title="Knowledge Manager", page_icon="📚", layout="wide")
st.title("📚 Knowledge Manager")
st.markdown("Upload and manage documents in your knowledge base.")

# ── Upload section ───────────────────────────────────────────
st.subheader("📤 Upload Documents")

col1, col2 = st.columns(2)
with col1:
    doc_type = st.selectbox(
        "Document Type",
        ["Change Request (CR)", "SRS Document", "Test Cases", "QA Issues"]
    )
with col2:
    uploaded_file = st.file_uploader("Choose PDF file", type=["pdf"])

TYPE_MAP = {
    "Change Request (CR)": ("cr",       config.CR_PATH,         config.COLLECTION_CRS),
    "SRS Document":        ("srs",      config.SRS_PATH,        config.COLLECTION_SRS),
    "Test Cases":          ("test_case",config.TEST_CASES_PATH, config.COLLECTION_TEST_CASES),
    "QA Issues":           ("qa_issue", config.QA_ISSUES_PATH,  config.COLLECTION_QA_ISSUES),
}

if uploaded_file and st.button("📥 Upload & Index", type="primary"):
    doc_type_key, folder_path, collection = TYPE_MAP[doc_type]
    save_path = folder_path / uploaded_file.name

    # Save to knowledge base folder
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner(f"Indexing {uploaded_file.name}..."):
        added = ingest_single_file(save_path, doc_type_key, collection)

    if added > 0:
        st.success(f"✅ Indexed {added} chunks from {uploaded_file.name}")
    else:
        st.warning("File already indexed or no text extracted.")

# ── Knowledge Base Status ────────────────────────────────────
st.markdown("---")
st.subheader("📊 Knowledge Base Status")

stats = get_collection_stats()
col1, col2, col3, col4, col5 = st.columns(5)
cols = [col1, col2, col3, col4, col5]
labels = ["CRs", "SRS", "Test Cases", "QA Issues", "Feedback"]
collections = [
    config.COLLECTION_CRS, config.COLLECTION_SRS,
    config.COLLECTION_TEST_CASES, config.COLLECTION_QA_ISSUES,
    config.COLLECTION_FEEDBACK
]

for col, label, coll in zip(cols, labels, collections):
    with col:
        st.metric(label, f"{stats.get(coll, 0)} chunks")

# ── Existing files ───────────────────────────────────────────
st.markdown("---")
st.subheader("📁 Files in Knowledge Base")

for label, (_, folder, _) in TYPE_MAP.items():
    files = list(folder.glob("*.pdf"))
    if files:
        with st.expander(f"{label} ({len(files)} files)"):
            for f in files:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f.name)
                with col2:
                    if st.button("🗑️", key=f"del_{f.name}"):
                        f.unlink()
                        st.success(f"Deleted {f.name}")
                        st.rerun()