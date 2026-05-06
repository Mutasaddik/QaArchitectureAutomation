import streamlit as st
from pathlib import Path
import sys
import re
import shutil
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ui_theme import inject_theme
inject_theme()

from src.ingestion.ingest_pipeline import ingest_single_file, get_ingestion_stats
from src.vectorstore.chroma_manager import get_collection_stats, delete_collection
import config

st.set_page_config(page_title="Knowledge Manager", page_icon="📚", layout="wide")
st.title("📚 Knowledge Manager")
st.markdown("Upload and manage documents in your knowledge base.")

# ── Naming Convention Guide ───────────────────────────────────
with st.expander("📌 File Naming Convention", expanded=False):
    st.markdown("""
    Use this naming format for all uploaded files:

    | Document Type | Format | Example |
    |---|---|---|
    | Change Request | `CR-{ID}-{short-title}.pdf` | `CR-2024-089-Weekly-Loan-Repayment.pdf` |
    | SRS Document | `SRS-{module}-{version}.pdf` | `SRS-Loan-Management-v1.2.pdf` |
    | Test Cases | `TC-{CR-ID}-{module}.pdf` | `TC-2024-089-Loan-Module.pdf` |
    | QA Issues | `QA-Issues-{module}.pdf` | `QA-Issues-Elasticsearch.pdf` |

    **Rules:**
    - Use hyphens `-` instead of spaces
    - No special characters (`?`, `&`, `#`, `%`)
    - Keep it short and descriptive
    - Always include version if available

    > ⚠️ Files with special characters in name will be auto-renamed on upload.
    """)

TYPE_MAP = {
    "Change Request (CR)":  ("cr",        config.CR_PATH,         config.COLLECTION_CRS),
    "SRS Document":         ("srs",       config.SRS_PATH,        config.COLLECTION_SRS),
    "Test Cases":           ("test_case", config.TEST_CASES_PATH, config.COLLECTION_TEST_CASES),
    "QA Issues":            ("qa_issue",  config.QA_ISSUES_PATH,  config.COLLECTION_QA_ISSUES),
}

TYPE_PREFIX = {
    "Change Request (CR)": "CR",
    "SRS Document":        "SRS",
    "Test Cases":          "TC",
    "QA Issues":           "QA-Issues",
}


def clean_filename(name: str) -> str:
    """Remove special characters and spaces from filename."""
    stem = Path(name).stem
    ext  = Path(name).suffix
    # Replace spaces and special chars with hyphens
    clean = re.sub(r'[^\w\-.]', '-', stem)
    # Remove multiple consecutive hyphens
    clean = re.sub(r'-+', '-', clean)
    clean = clean.strip('-')
    return f"{clean}{ext}"


# ── Upload Section ────────────────────────────────────────────
st.subheader("📤 Upload Document")

col1, col2 = st.columns(2)
with col1:
    doc_type = st.selectbox("Document Type", list(TYPE_MAP.keys()))
with col2:
    uploaded_file = st.file_uploader("Choose PDF file", type=["pdf"])

# Show naming suggestion
if doc_type:
    prefix = TYPE_PREFIX[doc_type]
    st.caption(f"💡 Suggested naming: `{prefix}-{{ID}}-{{short-description}}.pdf` — e.g. `{prefix}-001-Loan-Module.pdf`")

if uploaded_file:
    original_name = uploaded_file.name
    clean_name    = clean_filename(original_name)

    if original_name != clean_name:
        st.warning(f"⚠️ Filename has special characters. Will be saved as: **{clean_name}**")
    else:
        st.info(f"📄 File: **{clean_name}**")

    if st.button("📥 Upload & Index", type="primary"):
        doc_type_key, folder_path, collection = TYPE_MAP[doc_type]
        save_path = folder_path / clean_name

        # Save file
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        with st.spinner(f"Indexing {clean_name}..."):
            added = ingest_single_file(save_path, doc_type_key, collection)

        if added > 0:
            st.success(f"✅ Indexed {added} chunks from **{clean_name}**")
            st.balloons()
        else:
            # Force index if duplicate detected
            from src.ingestion.pdf_loader import build_documents
            from src.vectorstore.chroma_manager import add_documents_to_vectorstore
            docs  = build_documents(save_path, doc_type_key)
            added = add_documents_to_vectorstore(docs, collection, skip_duplicates=False)
            if added > 0:
                st.success(f"✅ Force indexed {added} chunks from **{clean_name}**")
            else:
                st.warning("No text could be extracted from this PDF.")

# ── Knowledge Base Status ─────────────────────────────────────
st.markdown("---")
st.subheader("📊 Knowledge Base Status")
stats = get_collection_stats()

col1, col2, col3, col4, col5 = st.columns(5)
cols        = [col1, col2, col3, col4, col5]
labels      = ["CRs", "SRS", "Test Cases", "QA Issues", "Feedback"]
collections = [
    config.COLLECTION_CRS, config.COLLECTION_SRS,
    config.COLLECTION_TEST_CASES, config.COLLECTION_QA_ISSUES,
    config.COLLECTION_FEEDBACK
]
for col, label, coll in zip(cols, labels, collections):
    count = stats.get(coll, 0)
    with col:
        if count > 0:
            st.metric(label, f"{count} chunks", delta="indexed")
        else:
            st.metric(label, "0 chunks")

# ── Files in Knowledge Base ───────────────────────────────────
st.markdown("---")
st.subheader("📁 Files in Knowledge Base")

any_files = False
for label, (_, folder, collection) in TYPE_MAP.items():
    files = list(folder.glob("*.pdf"))
    if files:
        any_files = True
        with st.expander(f"**{label}** ({len(files)} files)"):
            for f in files:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.text(f.name)
                with col2:
                    # Download button
                    with open(f, "rb") as file:
                        st.download_button(
                            "⬇️", file.read(),
                            file_name=f.name,
                            key=f"dl_{f.name}"
                        )
                with col3:
                    if st.button("🗑️", key=f"del_{f.name}"):
                        f.unlink()
                        st.success(f"Deleted {f.name}")
                        st.rerun()

if not any_files:
    st.info("No files uploaded yet. Upload PDFs above to build your knowledge base.")

# ── Danger Zone ───────────────────────────────────────────────
st.markdown("---")
with st.expander("⚠️ Danger Zone — Reset Knowledge Base"):
    st.warning("This will delete all indexed data from ChromaDB. Files on disk will NOT be deleted.")
    col1, col2 = st.columns(2)
    with col1:
        reset_type = st.selectbox("Reset which collection?",
            ["All"] + list(TYPE_MAP.keys()))
    with col2:
        if st.button("🔥 Reset Selected", type="primary"):
            if reset_type == "All":
                for _, (_, _, coll) in TYPE_MAP.items():
                    delete_collection(coll)
                st.success("All collections reset!")
            else:
                _, _, coll = TYPE_MAP[reset_type]
                delete_collection(coll)
                st.success(f"{reset_type} collection reset!")
            st.rerun()