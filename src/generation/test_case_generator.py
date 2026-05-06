# src/generation/test_case_generator.py
# Generates structured test cases from a CR + test plan summary.

from datetime import datetime
from pathlib import Path
from loguru import logger

import config
from src.retrieval.context_builder import build_test_case_context
from src.generation.prompts import QA_SYSTEM_PROMPT, build_test_case_prompt
from src.generation.llm_client import generate


def generate_test_cases(
    cr_text: str,
    test_plan_summary: str = "",
    stream: bool = False
) -> dict:
    """
    Generates detailed test cases for a given CR.

    cr_text:           full CR description
    test_plan_summary: optional — paste first few lines of test plan
                       so test cases align with the plan
    stream:            if True, tokens print live

    Returns dict with test_cases text + metadata.
    """
    logger.info("Starting test case generation...")

    # ── Step 1: Get similar existing test cases for format reference
    existing_tc_context = build_test_case_context(cr_text)

    # ── Step 2: Build prompt
    prompt = build_test_case_prompt(
        cr_text=cr_text,
        test_plan_summary=test_plan_summary or "Not provided.",
        existing_test_cases=existing_tc_context
    )
    logger.info(f"Test case prompt built ({len(prompt)} characters)")

    # ── Step 3: Send to LLM
    logger.info("Generating test cases via LLM...")
    test_cases = generate(
        prompt=prompt,
        system_prompt=QA_SYSTEM_PROMPT,
        temperature=0.2,
        stream=stream
    )

    result = {
        "test_cases":   test_cases,
        "cr_text":      cr_text,
        "generated_at": datetime.now().isoformat(),
        "model_used":   config.OLLAMA_LLM_MODEL,
    }

    logger.info("Test case generation complete!")
    return result


def save_test_cases(result: dict, filename: str = None) -> Path:
    """Save generated test cases to exports folder."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"test_cases_{timestamp}.txt"

    output_path = config.EXPORTS_PATH / filename
    content = f"""
QA ASSISTANT - GENERATED TEST CASES
=====================================
Generated At : {result['generated_at']}
Model Used   : {result['model_used']}
=====================================

CHANGE REQUEST:
{result['cr_text']}

=====================================
GENERATED TEST CASES:
=====================================
{result['test_cases']}
"""
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"Test cases saved to: {output_path}")
    return output_path


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    sample_cr = """
    CR-2024-089: Weekly Loan Repayment Support
    Add support for weekly repayment schedules.
    - Add 'weekly' option to repayment frequency dropdown
    - Recalculate installment amount based on weekly schedule
    - Update loan summary report
    - Notify borrower via SMS when weekly payment is due
    Affected Modules: Loan Management, Reporting, Notifications
    """

    sample_plan_summary = """
    Test Strategy: Regression + Integration
    High Risk: Repayment calculation logic
    In Scope: Loan module, Notification module
    """

    print("Generating test cases (30-60 seconds)...")
    print("=" * 60)

    result = generate_test_cases(sample_cr, sample_plan_summary, stream=True)

    print("\n" + "=" * 60)
    saved = save_test_cases(result)
    print(f"Saved to: {saved}")