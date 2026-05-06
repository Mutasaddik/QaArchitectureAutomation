import streamlit as st
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generation.test_plan_generator import generate_test_plan, save_test_plan
from src.feedback.feedback_manager import save_feedback
from src.ingestion.pdf_loader import extract_text_from_pdf

st.set_page_config(page_title="Test Plan Generator", page_icon="📋", layout="wide")
st.title("📋 Test Plan Generator")
st.markdown("Upload your CR or paste it below to generate a complete test plan.")

st.subheader("Step 1 — Provide the Change Request")
input_method = st.radio("How do you want to provide the CR?",
                         ["📝 Paste Text", "📄 Upload PDF"], horizontal=True)
cr_text = ""

if input_method == "📝 Paste Text":
    cr_text = st.text_area("Change Request (CR) Description", height=250,
        placeholder="Paste your full CR description here...\n\nExample:\nCR-2024-089: Add weekly repayment support\n- Add weekly option to frequency dropdown\n- Recalculate installment amounts\n- Send SMS notifications\nAffected Modules: Loan Management, Notifications\nPriority: High")
else:
    uploaded_cr = st.file_uploader("Upload CR PDF", type=["pdf"])
    if uploaded_cr:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_cr.read())
            tmp_path = Path(tmp.name)
        with st.spinner("Extracting text from PDF..."):
            pages = extract_text_from_pdf(tmp_path)
            cr_text = "\n\n".join(p["text"] for p in pages)
            tmp_path.unlink()
        if cr_text:
            st.success(f"Extracted {len(pages)} pages from PDF")
            with st.expander("Preview extracted text"):
                st.text(cr_text[:1000] + "..." if len(cr_text) > 1000 else cr_text)
        else:
            st.error("Could not extract text from PDF.")

st.subheader("Step 2 — Additional Instructions (Optional)")
additional_notes = st.text_area("Any specific focus areas or constraints?", height=100,
    placeholder="e.g. Focus on regression for payment module. Include boundary cases for amount fields.")

st.subheader("Step 3 — Generate")
col1, col2 = st.columns([2, 1])
with col1:
    generate_btn = st.button("🚀 Generate Test Plan", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear All", use_container_width=True):
        for key in ["tp_result", "tp_cr_text"]:
            st.session_state.pop(key, None)
        st.rerun()

if generate_btn:
    if not cr_text.strip():
        st.warning("Please provide a CR — paste text or upload a PDF.")
    else:
        full_input = cr_text
        if additional_notes.strip():
            full_input += f"\n\n=== ADDITIONAL INSTRUCTIONS ===\n{additional_notes}"
        with st.spinner("Generating test plan... (30-60 seconds)"):
            result = generate_test_plan(full_input, stream=False)
        st.session_state["tp_result"]  = result
        st.session_state["tp_cr_text"] = cr_text
        st.success("Test Plan Generated!")

if "tp_result" in st.session_state:
    result = st.session_state["tp_result"]
    st.markdown("---")
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
        correction = st.text_area("What should the correct output look like?", height=150)
    if st.button("Submit Feedback"):
        save_feedback(cr_text=st.session_state.get("tp_cr_text",""),
            generated_output=result["test_plan"], output_type="test_plan",
            rating=rating, correction=correction, comments=comments)
        st.success("Feedback saved!")