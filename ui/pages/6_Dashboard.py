# ui/pages/6_📊_Dashboard.py
import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vectorstore.chroma_manager import get_collection_stats
from src.feedback.feedback_manager import get_feedback_stats, get_all_feedback
from src.database.query_store import get_all_queries
import config

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard")
st.markdown("Overview of your QA Assistant knowledge base and usage.")

# ── Knowledge Base Stats ─────────────────────────────────────
st.subheader("📚 Knowledge Base")
stats = get_collection_stats()
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Change Requests", stats.get(config.COLLECTION_CRS, 0), "chunks")
with col2: st.metric("SRS Documents",   stats.get(config.COLLECTION_SRS, 0), "chunks")
with col3: st.metric("Test Cases",      stats.get(config.COLLECTION_TEST_CASES, 0), "chunks")
with col4: st.metric("QA Issues",       stats.get(config.COLLECTION_QA_ISSUES, 0), "chunks")

# ── Feedback Stats ───────────────────────────────────────────
st.markdown("---")
st.subheader("⭐ Feedback & Quality")
fb_stats = get_feedback_stats()
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Feedback",  fb_stats["total"])
with col2: st.metric("Average Rating",  f"{fb_stats['average']}/5")
with col3: st.metric("High Rated",      fb_stats["high_rated"])
with col4: st.metric("Low Rated",       fb_stats["low_rated"])

# ── Recent Feedback ──────────────────────────────────────────
feedback = get_all_feedback()
if feedback:
    st.markdown("---")
    st.subheader("📝 Recent Feedback")
    import pandas as pd
    df = pd.DataFrame(feedback)[["id","output_type","rating","comments","created_at"]]
    st.dataframe(df.tail(10), use_container_width=True)

# ── Query Repository Stats ───────────────────────────────────
st.markdown("---")
st.subheader("🔍 Query Repository")
queries = get_all_queries()
st.metric("Total Saved Queries", len(queries))
if queries:
    import pandas as pd
    df = pd.DataFrame(queries)[["title","module","cr_id","created_at"]]
    st.dataframe(df, use_container_width=True)

# ── Exports ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("📁 Recent Exports")
exports = list(config.EXPORTS_PATH.glob("*"))
exports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
if exports:
    for f in exports[:10]:
        col1, col2 = st.columns([4,1])
        with col1: st.text(f.name)
        with col2:
            with open(f, "rb") as file:
                st.download_button("⬇️", file.read(), f.name, key=f"exp_{f.name}")
else:
    st.info("No exports yet.")