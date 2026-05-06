import streamlit as st
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generation.test_case_generator import generate_test_cases
from src.export.excel_exporter import export_to_excel, parse_llm_test_cases
from src.feedback.feedback_manager import save_feedback

st.set_page_config(page_title="Test Case Generator", page_icon="🧪", layout="wide")
st.title("🧪 Test Case Generator")

if "tc_cr_text"      not in st.session_state: st.session_state["tc_cr_text"]      = ""
if "tc_result"       not in st.session_state: st.session_state["tc_result"]       = None
if "tc_approved"     not in st.session_state: st.session_state["tc_approved"]     = False
if "tc_conversation" not in st.session_state: st.session_state["tc_conversation"] = []

st.subheader("Step 1 — Provide the Change Request")
input_method = st.radio("Input method:", ["📝 Paste Text", "📄 Upload PDF"], horizontal=True)

cr_text = st.session_state["tc_cr_text"]
if input_method == "📝 Paste Text":
    cr_text = st.text_area("CR Description", value=st.session_state["tc_cr_text"], height=200,
        placeholder="Paste your CR here...")
    st.session_state["tc_cr_text"] = cr_text
else:
    uploaded_cr = st.file_uploader("Upload CR PDF", type=["pdf"])
    if uploaded_cr:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_cr.read())
            tmp_path = Path(tmp.name)
        with st.spinner("Extracting..."):
            from src.ingestion.pdf_loader import extract_text_from_pdf
            pages = extract_text_from_pdf(tmp_path)
            cr_text = "\n\n".join(p["text"] for p in pages)
            tmp_path.unlink()
        st.session_state["tc_cr_text"] = cr_text
        if cr_text:
            st.success(f"Extracted {len(pages)} pages")

st.subheader("Step 2 — Options")
additional_notes = st.text_area("Additional focus or instructions (optional):", height=80,
    placeholder="e.g. Add more negative cases. Focus on role-based scenarios for Admin and BAO users.")

col1, col2, col3 = st.columns(3)
with col1: project_name = st.text_input("Project Name", value="PROJECT")
with col2: cr_id = st.text_input("CR ID", value="CR-001")
with col3: tc_count = st.selectbox("Test cases count:", ["10-15", "15-20", "20-30", "30+"])

st.subheader("Step 3 — Generate")
st.info("System will generate test cases. Review them, refine if needed, then approve to export.")

col1, col2 = st.columns([2, 1])
with col1:
    generate_btn = st.button("🚀 Generate Test Cases", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Reset", use_container_width=True):
        for k in ["tc_cr_text","tc_result","tc_approved","tc_conversation"]:
            st.session_state.pop(k, None)
        st.rerun()

if generate_btn:
    if not st.session_state["tc_cr_text"].strip():
        st.warning("Please provide a CR first.")
    else:
        full_input = st.session_state["tc_cr_text"]
        if additional_notes.strip():
            full_input += f"\n\n=== ADDITIONAL FOCUS ===\n{additional_notes}"
        full_input += f"\n\n=== QUANTITY ===\nGenerate {tc_count} test cases."
        with st.spinner(f"Generating {tc_count} test cases..."):
            result = generate_test_cases(full_input, stream=False)
        st.session_state["tc_result"]   = result
        st.session_state["tc_approved"] = False
        st.session_state["tc_conversation"].append({"type":"generation","content":result["test_cases"],"notes":additional_notes})
        st.success("Test cases generated! Review below.")

if st.session_state["tc_result"]:
    result = st.session_state["tc_result"]
    st.markdown("---")
    st.subheader("📋 Generated Test Cases")
    st.markdown(result["test_cases"])

    rows = parse_llm_test_cases(result["test_cases"])
    if rows:
        import pandas as pd
        st.markdown(f"**Parsed {len(rows)} test cases:**")
        df = pd.DataFrame(rows)
        st.dataframe(df[["Folder","Name","Priority"]], use_container_width=True)

    st.markdown("---")
    st.subheader("💬 Refine Test Cases")
    st.markdown("Not satisfied? Describe what needs to change and regenerate.")

    for msg in st.session_state["tc_conversation"]:
        if msg["type"] == "feedback":
            with st.chat_message("user"):
                st.markdown(f"**Feedback:** {msg['content']}")

    refinement = st.text_area("What should be changed?", height=80,
        placeholder="e.g. Add more negative cases. Steps in TC-3 are too vague. Add boundary cases for date fields.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate with Feedback"):
            if refinement.strip():
                full_input = st.session_state["tc_cr_text"]
                full_input += f"\n\n=== FEEDBACK TO FIX ===\n{refinement}"
                full_input += f"\n\n=== QUANTITY ===\nGenerate {tc_count} test cases."
                with st.spinner("Regenerating..."):
                    new_result = generate_test_cases(full_input, stream=False)
                save_feedback(cr_text=st.session_state["tc_cr_text"],
                    generated_output=result["test_cases"], output_type="test_case",
                    rating=2, correction=refinement, comments="User requested regeneration")
                st.session_state["tc_result"] = new_result
                st.session_state["tc_conversation"].append({"type":"feedback","content":refinement})
                st.rerun()
            else:
                st.warning("Please describe what needs to change.")
    with col2:
        if st.button("✅ Approve & Export", type="primary"):
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
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download Excel", data=f.read(),
                        file_name=path.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col2:
            st.download_button("⬇️ Download TXT", data=result["test_cases"],
                file_name=f"test_cases_{cr_id}.txt", mime="text/plain", use_container_width=True)

        st.markdown("---")
        st.subheader("⭐ Final Feedback")
        final_rating = st.slider("Final Rating", 1, 5, 4)
        final_comments = st.text_input("Final Comments")
        final_correction = ""
        if final_rating <= 2:
            final_correction = st.text_area("What was wrong? (remembered for next time)", height=100)
        if st.button("Submit Final Feedback"):
            save_feedback(cr_text=st.session_state["tc_cr_text"],
                generated_output=result["test_cases"], output_type="test_case",
                rating=final_rating, correction=final_correction, comments=final_comments)
            st.success("Feedback saved and remembered!")