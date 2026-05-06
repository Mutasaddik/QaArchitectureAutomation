# src/generation/test_plan_generator.py
# This is the core generator that produces test plans.
# It combines: CR text → context retrieval → prompt → LLM → output

from datetime import datetime
from pathlib import Path
from loguru import logger

import config
from src.retrieval.context_builder import build_context_string, build_full_context
from src.generation.prompts import (
    QA_SYSTEM_PROMPT,
    build_test_plan_prompt,
    build_clarification_prompt
)
from src.generation.llm_client import generate


def generate_test_plan(cr_text: str, stream: bool = False) -> dict:
    """
    Main function — generates a complete test plan for a given CR.

    cr_text: the full CR description (pasted text or extracted from PDF)
    stream:  if True, tokens print live to terminal

    Returns a dict with:
    - test_plan:   the generated test plan text
    - context:     what knowledge base context was used
    - cr_text:     original CR text
    - generated_at: timestamp
    """
    logger.info("Starting test plan generation...")

    # ── Step 1: Retrieve relevant context from knowledge base ─
    logger.info("Retrieving context from knowledge base...")
    full_context = build_full_context(cr_text)

    # Combine all context sections into one string for the prompt
    context_string = "\n\n".join([
        full_context["similar_crs"],
        full_context["srs_context"],
        full_context["qa_issues"],
        full_context["test_cases"],
    ])

    # ── Step 2: Build the prompt ──────────────────────────────
    prompt = build_test_plan_prompt(cr_text, context_string)
    logger.info(f"Prompt built ({len(prompt)} characters)")

    # ── Step 3: Send to LLM ───────────────────────────────────
    logger.info("Sending to LLM for generation...")
    test_plan = generate(
        prompt=prompt,
        system_prompt=QA_SYSTEM_PROMPT,
        temperature=0.2,   # low temp = focused, consistent output
        stream=stream
    )

    # ── Step 4: Return structured result ─────────────────────
    result = {
        "test_plan":    test_plan,
        "context_used": full_context,
        "cr_text":      cr_text,
        "generated_at": datetime.now().isoformat(),
        "model_used":   config.OLLAMA_LLM_MODEL,
    }

    logger.info("Test plan generation complete!")
    return result


def generate_clarification_questions(cr_text: str) -> str:
    """
    Before generating a test plan, analyze the CR for gaps.
    Returns a list of clarification questions to ask the dev/BA.
    Useful when CR is vague or incomplete.
    """
    logger.info("Analyzing CR for clarification needs...")
    prompt = build_clarification_prompt(cr_text)
    result = generate(
        prompt=prompt,
        system_prompt=QA_SYSTEM_PROMPT,
        temperature=0.3
    )
    return result


def save_test_plan(result: dict, filename: str = None) -> Path:
    """
    Saves the generated test plan as a .txt file in the exports folder.
    filename: optional custom name, otherwise auto-generated from timestamp
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_plan_{timestamp}.txt"

    output_path = config.EXPORTS_PATH / filename

    content = f"""
QA ASSISTANT - GENERATED TEST PLAN
====================================
Generated At : {result['generated_at']}
Model Used   : {result['model_used']}
====================================

CHANGE REQUEST:
{result['cr_text']}

====================================
GENERATED TEST PLAN:
====================================
{result['test_plan']}
"""
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"Test plan saved to: {output_path}")
    return output_path


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    sample_cr = """
    CR-2024-089: Weekly Loan Repayment Support

    Currently the system only supports monthly loan repayments.
    This CR adds support for weekly repayment schedules.

    Changes:
    - Add 'weekly' option to repayment frequency dropdown
    - Recalculate installment amount based on weekly schedule
    - Update loan summary report to show weekly breakdown
    - Notify borrower via SMS when weekly payment is due

    Affected Modules: Loan Management, Reporting, Notifications
    Priority: High
    """

    print("Generating test plan (this may take 30-60 seconds)...")
    print("=" * 60)

    result = generate_test_plan(sample_cr, stream=True)

    print("\n" + "=" * 60)
    print("Saving test plan...")
    saved_path = save_test_plan(result)
    print(f"Saved to: {saved_path}")