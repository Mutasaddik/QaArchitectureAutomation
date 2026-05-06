import streamlit as st
from pathlib import Path
import sys, tempfile, time
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ui_theme import inject_theme
inject_theme()

from src.generation.background_runner import run_test_plan_in_background, get_job
from src.generation.test_plan_generator import save_test_plan
from src.feedback.feedback_manager import save_feedback
from src.ingestion.pdf_loader import extract_text_from_pdf

st.set_page_config(page_title="Test Plan Generator", page_icon="📋", layout="wide")
st.title("📋 Test Plan Generator")
st.info("⚡ Generation runs in background — you can switch pages and come back anytime!")

if "tp_job_id"  not in st.session_state: st.session_state["tp_job_id"]  = None
if "tp_cr_text" not in st.session_state: st.session_state["tp_cr_text"] = ""
if "tp_result"  not in st.session_state: st.session_state["tp_result"]  = None

st.subheader("Step 1 — Provide CR")
method = st.radio("Input:", ["📝 Paste Text", "📄 Upload PDF"], horizontal=True)
cr_text = st.session_state["tp_cr_text"]

if method == "📝 Paste Text":
    cr_text = st.text_area("CR Description", value=cr_text, height=250,
        placeholder="Paste your CR here...")
    st.session_state["tp_cr_text"] = cr_text
else:
    f = st.file_uploader("Upload CR PDF", type=["pdf"])
    if f:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(f.read()); tmp_path = Path(tmp.name)
        with st.spinner("Extracting..."):
            pages = extract_text_from_pdf(tmp_path)
            cr_text = "\n\n".join(p["text"] for p in pages)
            tmp_path.unlink()
        st.session_state["tp_cr_text"] = cr_text
        if cr_text:
            st.success(f"Extracted {len(pages)} pages")
            with st.expander("Preview"): st.text(cr_text[:800])

notes = st.text_area("Additional Instructions (optional):", height=80,
    placeholder="e.g. Focus on regression. Include boundary cases.")

st.subheader("Step 2 — Generate")
col1, col2 = st.columns([2,1])
with col1:
    gen_btn = st.button("🚀 Generate Test Plan", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        for k in ["tp_job_id","tp_cr_text","tp_result"]: st.session_state.pop(k,None)
        st.rerun()

if gen_btn:
    if not st.session_state["tp_cr_text"].strip():
        st.warning("Please provide a CR first.")
    else:
        inp = st.session_state["tp_cr_text"]
        if notes.strip(): inp += f"\n\n=== ADDITIONAL ===\n{notes}"
        job_id = f"tp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state["tp_job_id"] = job_id
        st.session_state["tp_result"] = None
        run_test_plan_in_background(job_id, inp)
        st.success("✅ Started! You can switch pages and come back.")
        st.rerun()

if st.session_state["tp_job_id"] and not st.session_state["tp_result"]:
    job = get_job(st.session_state["tp_job_id"])
    st.markdown("---")
    if job["status"] == "running":
        st.warning("⏳ Generating in background...")
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("🔄 Refresh Status"): st.rerun()
        time.sleep(3); st.rerun()
    elif job["status"] == "done":
        st.session_state["tp_result"] = job["result"]
        st.rerun()
    elif job["status"] == "error":
        st.error(f"Failed: {job.get('error','Unknown')}")
        st.session_state["tp_job_id"] = None

if st.session_state["tp_result"]:
    result = st.session_state["tp_result"]
    st.markdown("---")
    st.success("✅ Test Plan Ready!")
    st.subheader("📄 Generated Test Plan")
    st.markdown(result["test_plan"])
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save to Exports"):
            path = save_test_plan(result)
            st.success(f"Saved: {path.name}")
    with col2:
        st.download_button("⬇️ Download TXT", data=result["test_plan"],
            file_name="test_plan.txt", mime="text/plain")
    st.markdown("---")
    st.subheader("⭐ Feedback")
    rating = st.slider("Rating", 1, 5, 4)
    comments = st.text_input("Comments")
    correction = ""
    if rating <= 2:
        correction = st.text_area("Correct version:", height=150)
    if st.button("Submit Feedback"):
        save_feedback(cr_text=st.session_state.get("tp_cr_text",""),
            generated_output=result["test_plan"], output_type="test_plan",
            rating=rating, correction=correction, comments=comments)
        st.success("Feedback saved!")