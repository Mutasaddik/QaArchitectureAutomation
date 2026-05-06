import streamlit as st
from pathlib import Path
import sys, tempfile, time
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ui_theme import inject_theme
inject_theme()

from src.generation.background_runner import run_test_cases_in_background, get_job
from src.export.excel_exporter import export_to_excel, parse_llm_test_cases
from src.feedback.feedback_manager import save_feedback
from src.ingestion.pdf_loader import extract_text_from_pdf

st.set_page_config(page_title="Test Case Generator", page_icon="🧪", layout="wide")
st.title("🧪 Test Case Generator")
st.info("⚡ Generation runs in background — switch pages freely and come back!")

if "tc_job_id"       not in st.session_state: st.session_state["tc_job_id"]       = None
if "tc_cr_text"      not in st.session_state: st.session_state["tc_cr_text"]      = ""
if "tc_result"       not in st.session_state: st.session_state["tc_result"]       = None
if "tc_approved"     not in st.session_state: st.session_state["tc_approved"]     = False
if "tc_conversation" not in st.session_state: st.session_state["tc_conversation"] = []

st.subheader("Step 1 — Provide CR")
method = st.radio("Input:", ["📝 Paste Text", "📄 Upload PDF"], horizontal=True)
cr_text = st.session_state["tc_cr_text"]

if method == "📝 Paste Text":
    cr_text = st.text_area("CR Description", value=cr_text, height=200,
        placeholder="Paste your CR here...")
    st.session_state["tc_cr_text"] = cr_text
else:
    f = st.file_uploader("Upload CR PDF", type=["pdf"])
    if f:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(f.read()); tmp_path = Path(tmp.name)
        with st.spinner("Extracting..."):
            pages = extract_text_from_pdf(tmp_path)
            cr_text = "\n\n".join(p["text"] for p in pages)
            tmp_path.unlink()
        st.session_state["tc_cr_text"] = cr_text
        if cr_text: st.success(f"Extracted {len(pages)} pages")

st.subheader("Step 2 — Options")
notes = st.text_area("Additional focus (optional):", height=80,
    placeholder="e.g. More negative cases. Role-based scenarios for Admin and BAO.")
col1, col2, col3 = st.columns(3)
with col1: project_name = st.text_input("Project Name", value="PROJECT")
with col2: cr_id        = st.text_input("CR ID", value="CR-001")
with col3: tc_count     = st.selectbox("Count:", ["10-15","15-20","20-30","30+"])

st.subheader("Step 3 — Generate")
col1, col2 = st.columns([2,1])
with col1:
    gen_btn = st.button("🚀 Generate Test Cases", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Reset", use_container_width=True):
        for k in ["tc_job_id","tc_cr_text","tc_result","tc_approved","tc_conversation"]:
            st.session_state.pop(k,None)
        st.rerun()

if gen_btn:
    if not st.session_state["tc_cr_text"].strip():
        st.warning("Please provide a CR first.")
    else:
        inp = st.session_state["tc_cr_text"]
        if notes.strip(): inp += f"\n\n=== ADDITIONAL FOCUS ===\n{notes}"
        inp += f"\n\n=== QUANTITY ===\nGenerate {tc_count} test cases."
        job_id = f"tc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state["tc_job_id"]       = job_id
        st.session_state["tc_result"]       = None
        st.session_state["tc_approved"]     = False
        st.session_state["tc_conversation"] = []
        run_test_cases_in_background(job_id, inp)
        st.success("✅ Started! Switch pages freely and come back.")
        st.rerun()

if st.session_state["tc_job_id"] and not st.session_state["tc_result"]:
    job = get_job(st.session_state["tc_job_id"])
    st.markdown("---")
    if job["status"] == "running":
        st.warning("⏳ Generating test cases in background...")
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("🔄 Refresh Status"): st.rerun()
        time.sleep(3); st.rerun()
    elif job["status"] == "done":
        st.session_state["tc_result"] = job["result"]
        st.rerun()
    elif job["status"] == "error":
        st.error(f"Failed: {job.get('error','Unknown')}")
        st.session_state["tc_job_id"] = None

if st.session_state["tc_result"]:
    result = st.session_state["tc_result"]
    st.markdown("---")
    st.success("✅ Test Cases Ready!")
    st.subheader("📋 Generated Test Cases")
    st.markdown(result["test_cases"])

    rows = parse_llm_test_cases(result["test_cases"])
    if rows:
        import pandas as pd
        st.markdown(f"**Parsed {len(rows)} test cases:**")
        st.dataframe(pd.DataFrame(rows)[["Folder","Name","Priority"]], use_container_width=True)

    st.markdown("---")
    st.subheader("💬 Refine")
    for msg in st.session_state["tc_conversation"]:
        if msg["type"] == "feedback":
            with st.chat_message("user"):
                st.markdown(f"**Feedback:** {msg['content']}")

    refinement = st.text_area("What should be changed?", height=80,
        placeholder="e.g. Add more negative cases. Steps are too vague.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate with Feedback"):
            if refinement.strip():
                inp  = st.session_state["tc_cr_text"]
                inp += f"\n\n=== FEEDBACK ===\n{refinement}"
                inp += f"\n\n=== QUANTITY ===\nGenerate {tc_count} test cases."
                job_id = f"tc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                save_feedback(cr_text=st.session_state["tc_cr_text"],
                    generated_output=result["test_cases"], output_type="test_case",
                    rating=2, correction=refinement, comments="Regeneration")
                st.session_state["tc_job_id"]   = job_id
                st.session_state["tc_result"]   = None
                st.session_state["tc_approved"] = False
                st.session_state["tc_conversation"].append({"type":"feedback","content":refinement})
                run_test_cases_in_background(job_id, inp)
                st.success("Regenerating in background...")
                st.rerun()
            else:
                st.warning("Describe what needs to change.")
    with col2:
        if st.button("✅ Approve and Export", type="primary"):
            st.session_state["tc_approved"] = True
            st.rerun()

    if st.session_state["tc_approved"]:
        st.markdown("---")
        st.success("Approved! Ready to export.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Export to Excel", type="primary", use_container_width=True):
                path = export_to_excel(raw_llm_output=result["test_cases"],
                    cr_id=cr_id, project_name=project_name)
                with open(path,"rb") as f:
                    st.download_button("⬇️ Download Excel", data=f.read(),
                        file_name=path.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col2:
            st.download_button("⬇️ Download TXT", data=result["test_cases"],
                file_name=f"test_cases_{cr_id}.txt", mime="text/plain",
                use_container_width=True)

        st.markdown("---")
        st.subheader("⭐ Final Feedback")
        rating = st.slider("Rating", 1, 5, 4)
        comments = st.text_input("Comments")
        correction = ""
        if rating <= 2:
            correction = st.text_area("What was wrong?", height=100)
        if st.button("Submit Feedback"):
            save_feedback(cr_text=st.session_state["tc_cr_text"],
                generated_output=result["test_cases"], output_type="test_case",
                rating=rating, correction=correction, comments=comments)
            st.success("Feedback saved and remembered!")