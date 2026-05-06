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
from src.export.pdf_test_plan_exporter import generate_test_plan_pdf

st.set_page_config(page_title="Test Plan Generator", page_icon="📋", layout="wide")
st.title("📋 Test Plan Generator")
st.info("⚡ Generation runs in background — switch pages freely and come back anytime!")

if "tp_job_id"   not in st.session_state: st.session_state["tp_job_id"]   = None
if "tp_cr_text"  not in st.session_state: st.session_state["tp_cr_text"]  = ""
if "tp_result"   not in st.session_state: st.session_state["tp_result"]   = None
if "tp_pdf_path" not in st.session_state: st.session_state["tp_pdf_path"] = None

# ── Step 1: CR Input ──────────────────────────────────────────
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

# ── Step 2: Metadata ──────────────────────────────────────────
st.subheader("Step 2 — Document Info")
col1, col2, col3 = st.columns(3)
with col1: cr_id   = st.text_input("CR / JIRA ID", value="CR-001")
with col2: author  = st.text_input("Author", value="Senior QA Engineer")
with col3: version = st.text_input("Version", value="1.0.0")

notes = st.text_area("Additional Instructions (optional):", height=80,
    placeholder="e.g. Focus on regression. Include boundary cases.")

# ── Step 3: Generate ──────────────────────────────────────────
st.subheader("Step 3 — Generate")
col1, col2 = st.columns([2,1])
with col1:
    gen_btn = st.button("🚀 Generate Test Plan", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        for k in ["tp_job_id","tp_cr_text","tp_result","tp_pdf_path"]:
            st.session_state.pop(k, None)
        st.rerun()

if gen_btn:
    if not st.session_state["tp_cr_text"].strip():
        st.warning("Please provide a CR first.")
    else:
        inp = st.session_state["tp_cr_text"]
        if notes.strip():
            inp += f"\n\n=== ADDITIONAL INSTRUCTIONS ===\n{notes}"
        job_id = f"tp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state["tp_job_id"]   = job_id
        st.session_state["tp_result"]   = None
        st.session_state["tp_pdf_path"] = None
        run_test_plan_in_background(job_id, inp)
        st.success("✅ Started! You can switch pages and come back.")
        st.rerun()

# ── Step 4: Check Status ──────────────────────────────────────
if st.session_state["tp_job_id"] and not st.session_state["tp_result"]:
    job = get_job(st.session_state["tp_job_id"])
    st.markdown("---")
    if job["status"] == "running":
        st.warning("⏳ Generating in background...")
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("🔄 Refresh"): st.rerun()
        time.sleep(3); st.rerun()
    elif job["status"] == "done":
        st.session_state["tp_result"] = job["result"]
        st.rerun()
    elif job["status"] == "error":
        st.error(f"Failed: {job.get('error','Unknown')}")
        st.session_state["tp_job_id"] = None

# ── Step 5: Display & Export ──────────────────────────────────
if st.session_state["tp_result"]:
    result = st.session_state["tp_result"]
    st.markdown("---")
    st.success("✅ Test Plan Ready!")

    # ── Export buttons ────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Generate Professional PDF", type="primary", use_container_width=True):
            with st.spinner("Creating PDF..."):
                try:
                    # Get CR title from first line
                    first_line = st.session_state["tp_cr_text"].split("\n")[0][:60]
                    pdf_path = generate_test_plan_pdf(
                        test_plan_text = result["test_plan"],
                        cr_id          = cr_id,
                        cr_title       = first_line,
                        author         = author,
                        version        = version
                    )
                    st.session_state["tp_pdf_path"] = str(pdf_path)
                    st.success(f"PDF created: {pdf_path.name}")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

    with col2:
        st.download_button("⬇️ Download TXT",
            data=result["test_plan"],
            file_name=f"TestPlan_{cr_id}.txt",
            mime="text/plain",
            use_container_width=True)

    with col3:
        if st.session_state["tp_pdf_path"]:
            pdf_path = Path(st.session_state["tp_pdf_path"])
            if pdf_path.exists():
                with open(pdf_path, "rb") as pf:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=pf.read(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        use_container_width=True
                    )

    # ── Preview ───────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📄 Test Plan Preview")
    st.markdown(result["test_plan"])

    # ── Feedback ──────────────────────────────────────────────
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