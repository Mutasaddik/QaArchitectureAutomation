import streamlit as st
from pathlib import Path
import sys
import requests
sys.path.insert(0, str(Path(__file__).parent))

from src.ui_theme import inject_theme
from src.session_manager import load_session, save_session, clear_session, get_session_info

st.set_page_config(
    page_title="QA Assistant — Home",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_theme()

# ── Restore session ───────────────────────────────
if "session_restored" not in st.session_state:
    saved = load_session()
    if saved:
        for key in ["tp_cr_text","tp_result","tp_job_id","tc_cr_text",
                    "tc_result","tc_approved","tc_conversation","chat_cr_text"]:
            if saved.get(key):
                st.session_state[key] = saved[key]
    st.session_state["session_restored"] = True

def _auto_save():
    save_session({
        "tp_cr_text":      st.session_state.get("tp_cr_text", ""),
        "tp_result":       st.session_state.get("tp_result"),
        "tp_job_id":       st.session_state.get("tp_job_id"),
        "tc_cr_text":      st.session_state.get("tc_cr_text", ""),
        "tc_result":       st.session_state.get("tc_result"),
        "tc_approved":     st.session_state.get("tc_approved", False),
        "tc_conversation": st.session_state.get("tc_conversation", []),
        "chat_cr_text":    st.session_state.get("chat_cr_text", ""),
    })
_auto_save()

# ── Sidebar branding ──────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 1rem 1.25rem 1rem; margin-bottom:0.5rem;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#4f8ef7,#38bdf8);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;">🧪</div>
            <div>
                <div style="font-weight:700;font-size:0.95rem;color:#f0ece3;letter-spacing:-0.02em;">QA Assistant</div>
                <div style="font-size:0.65rem;color:#5c5852;text-transform:uppercase;letter-spacing:0.1em;margin-top:1px;">AI-POWERED TESTING</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Get all stats ─────────────────────────────────
try:
    from src.vectorstore.chroma_manager import get_collection_stats
    import config
    stats     = get_collection_stats()
    cr_count  = stats.get(config.COLLECTION_CRS, 0)
    tc_count  = stats.get(config.COLLECTION_TEST_CASES, 0)
    srs_count = stats.get(config.COLLECTION_SRS, 0)
    qi_count  = stats.get(config.COLLECTION_QA_ISSUES, 0)
    total_kb  = sum(stats.values())
except:
    cr_count = tc_count = srs_count = qi_count = total_kb = 0

try:
    from src.feedback.feedback_manager import get_feedback_stats, get_all_feedback
    fb       = get_feedback_stats()
    fb_total = fb["total"]
    fb_avg   = fb["average"]
    fb_list  = get_all_feedback()
except:
    fb_total = 0; fb_avg = 0; fb_list = []

try:
    from src.database.query_store import get_all_queries, get_all_modules
    queries      = get_all_queries()
    query_count  = len(queries)
    modules_list = get_all_modules()
except:
    query_count = 0; queries = []; modules_list = []

try:
    exports = sorted(
        [f for f in Path("exports").iterdir() if f.is_file()],
        key=lambda x: x.stat().st_mtime, reverse=True
    )
except:
    exports = []

# ── Page header ───────────────────────────────────
st.markdown("""
<div style="padding:0.5rem 0 1.75rem 0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:2rem;">
    <h1 style="font-size:1.6rem;font-weight:700;color:#f0ece3;letter-spacing:-0.03em;margin-bottom:4px;">
        Welcome back 👋
    </h1>
    <p style="color:#5c5852;font-size:0.875rem;margin:0;">Your AI-powered QA testing platform — overview & quick access</p>
</div>
""", unsafe_allow_html=True)

# ── Knowledge Base Stats ──────────────────────────
st.markdown('<p style="color:#5c5852;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">📚 KNOWLEDGE BASE</p>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Change Requests",  cr_count,    "uploaded CRs")
with col2: st.metric("SRS Documents",    srs_count,   "uploaded SRS")
with col3: st.metric("Test Cases",       tc_count,    "indexed cases")
with col4: st.metric("QA Issues",        qi_count,    "known issues")
with col5: st.metric("SQL Queries",      query_count, "saved queries")

st.markdown("<div style='margin:1.5rem 0;border-top:1px solid rgba(255,255,255,0.06);'></div>", unsafe_allow_html=True)

# ── Feedback Stats ────────────────────────────────
st.markdown('<p style="color:#5c5852;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">⭐ FEEDBACK & QUALITY</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Feedback",   fb_total)
with col2: st.metric("Average Rating",   f"{fb_avg}/5" if fb_avg else "—")
with col3: st.metric("High Rated (4-5)", fb["high_rated"] if fb_total else 0)
with col4: st.metric("Low Rated (1-2)",  fb["low_rated"]  if fb_total else 0)

st.markdown("<div style='margin:1.5rem 0;border-top:1px solid rgba(255,255,255,0.06);'></div>", unsafe_allow_html=True)

# ── Quick Actions ─────────────────────────────────
st.markdown('<p style="color:#5c5852;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">⚡ QUICK ACTIONS</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""<div class="qa-card" style="border-top:2px solid #4f8ef7;">
        <div style="font-size:1.3rem;margin-bottom:0.6rem;">📋</div>
        <div style="font-weight:600;color:#f0ece3;font-size:0.9rem;margin-bottom:0.3rem;">Test Plan Generator</div>
        <div style="font-size:0.8rem;color:#5c5852;">Generate complete test plans from CR documents</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Open →", key="btn_tp", use_container_width=True):
        st.switch_page("pages/1_Test_Plan_Generator.py")

with col2:
    st.markdown("""<div class="qa-card" style="border-top:2px solid #38bdf8;">
        <div style="font-size:1.3rem;margin-bottom:0.6rem;">🧪</div>
        <div style="font-weight:600;color:#f0ece3;font-size:0.9rem;margin-bottom:0.3rem;">Test Case Generator</div>
        <div style="font-size:0.8rem;color:#5c5852;">Structured test cases in your Excel format</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Open →", key="btn_tc", use_container_width=True):
        st.switch_page("pages/2_Test_Case_Generator.py")

with col3:
    st.markdown("""<div class="qa-card" style="border-top:2px solid #8b5cf6;">
        <div style="font-size:1.3rem;margin-bottom:0.6rem;">💬</div>
        <div style="font-weight:600;color:#f0ece3;font-size:0.9rem;margin-bottom:0.3rem;">Chat Assistant</div>
        <div style="font-size:0.8rem;color:#5c5852;">Ask anything about your CR documents</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Open →", key="btn_chat", use_container_width=True):
        st.switch_page("pages/3_Chat_Assistant.py")

col4, col5, col6 = st.columns(3)
with col4:
    st.markdown("""<div class="qa-card" style="border-top:2px solid #22c55e;">
        <div style="font-size:1.3rem;margin-bottom:0.6rem;">📚</div>
        <div style="font-weight:600;color:#f0ece3;font-size:0.9rem;margin-bottom:0.3rem;">Knowledge Manager</div>
        <div style="font-size:0.8rem;color:#5c5852;">Upload and index CR, SRS, test case files</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Open →", key="btn_km", use_container_width=True):
        st.switch_page("pages/4_Knowledge_Manager.py")

with col5:
    st.markdown("""<div class="qa-card" style="border-top:2px solid #f59e0b;">
        <div style="font-size:1.3rem;margin-bottom:0.6rem;">🔍</div>
        <div style="font-weight:600;color:#f0ece3;font-size:0.9rem;margin-bottom:0.3rem;">Query Repository</div>
        <div style="font-size:0.8rem;color:#5c5852;">Store and search SQL validation queries</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Open →", key="btn_qr", use_container_width=True):
        st.switch_page("pages/5_Query_Repository.py")

with col6:
    st.markdown("""<div class="qa-card" style="border-top:2px solid #14b8a6;">
        <div style="font-size:1.3rem;margin-bottom:0.6rem;">📁</div>
        <div style="font-weight:600;color:#f0ece3;font-size:0.9rem;margin-bottom:0.3rem;">Recent Exports</div>
        <div style="font-size:0.8rem;color:#5c5852;">{} files generated</div>
    </div>""".format(len(exports)), unsafe_allow_html=True)
    if exports:
        with st.expander("View exports"):
            for f in exports[:5]:
                col_a, col_b = st.columns([4,1])
                with col_a: st.text(f.name)
                with col_b:
                    with open(f,"rb") as file:
                        st.download_button("⬇️", file.read(), f.name, key=f"exp_{f.name}")

st.markdown("<div style='margin:1.5rem 0;border-top:1px solid rgba(255,255,255,0.06);'></div>", unsafe_allow_html=True)

# ── Recent Feedback table ─────────────────────────
if fb_list:
    st.markdown('<p style="color:#5c5852;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">📝 RECENT FEEDBACK</p>', unsafe_allow_html=True)
    import pandas as pd
    df = pd.DataFrame(fb_list)[["output_type","rating","comments","created_at"]].tail(5)
    df.columns = ["Type", "Rating", "Comments", "Date"]
    df["Date"] = df["Date"].str[:16].str.replace("T"," ")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("<div style='margin:1rem 0;'></div>", unsafe_allow_html=True)

# ── System status ─────────────────────────────────
st.markdown('<p style="color:#5c5852;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">🔌 SYSTEM STATUS</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = [m["name"] for m in r.json().get("models",[])] if r.status_code==200 else []
        st.success(f"✅ Ollama — {len(models)} models available")
    except:
        st.error("❌ Ollama not running")
with col2:
    st.success(f"✅ ChromaDB — {total_kb} total document chunks")
with col3:
    st.success(f"✅ Feedback DB — {fb_total} entries")

# ── Session info ──────────────────────────────────
info = get_session_info()
if info["exists"]:
    saved_at = info["saved_at"][:16].replace("T"," ")
    col1, col2 = st.columns([4,1])
    with col1:
        st.markdown(f'<p style="color:#5c5852;font-size:0.78rem;margin-top:1rem;">💾 Last session saved: {saved_at}</p>', unsafe_allow_html=True)
    with col2:
        if st.button("Clear Session", key="clear_session"):
            clear_session()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()