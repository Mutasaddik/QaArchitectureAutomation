# src/retrieval/context_builder.py
# This file takes raw ChromaDB search results and builds
# a clean, structured context string for the LLM prompt.
# Think of it as the "bridge" between search results and the AI.

from typing import Dict, List, Any
from loguru import logger

import config
from src.vectorstore.embedder import search_all_collections, search_qa_issues


def format_single_result(result: Dict[str, Any], index: int) -> str:
    """
    Formats one search result chunk into readable text.
    Each chunk shows its source file and content.
    """
    source   = result.get("source", "unknown")
    doc_type = result.get("doc_type", "unknown")
    content  = result.get("content", "").strip()
    return f"[{index}] Source: {source} (Type: {doc_type})\n{content}"


def build_cr_context(query: str) -> str:
    """
    Searches past CRs and formats results as context.
    Used to show the LLM what similar past CRs looked like.
    """
    from src.vectorstore.embedder import search_similar_crs
    results = search_similar_crs(query, n_results=3)

    if not results:
        return "No similar past Change Requests found in knowledge base."

    lines = ["=== Similar Past Change Requests ==="]
    for i, r in enumerate(results, 1):
        lines.append(format_single_result(r, i))
        lines.append("-" * 40)

    return "\n".join(lines)


def build_test_case_context(query: str) -> str:
    """
    Searches existing test cases and formats results as context.
    Helps the LLM follow your QA team's test case format and standards.
    """
    from src.vectorstore.embedder import search_similar_test_cases
    results = search_similar_test_cases(query, n_results=5)

    if not results:
        return "No similar test cases found in knowledge base."

    lines = ["=== Similar Existing Test Cases ==="]
    for i, r in enumerate(results, 1):
        lines.append(format_single_result(r, i))
        lines.append("-" * 40)

    return "\n".join(lines)


def build_qa_issues_context(query: str) -> str:
    """
    Always fetches known QA environment issues.
    These are ALWAYS injected into every test plan generation
    so the LLM knows about infra problems, ES sync issues, etc.
    """
    results = search_qa_issues(query, n_results=5)

    if not results:
        return (
            "No QA environment issues found in knowledge base.\n"
            "Consider adding known issues to knowledge_base/qa_issues/"
        )

    lines = ["=== Known QA Environment Issues ==="]
    lines.append("IMPORTANT: Consider these known issues when generating test plans.")
    lines.append("-" * 40)
    for i, r in enumerate(results, 1):
        lines.append(format_single_result(r, i))
        lines.append("-" * 40)

    return "\n".join(lines)


def build_srs_context(query: str) -> str:
    """
    Searches SRS documents for relevant requirements.
    Helps the LLM understand acceptance criteria and business rules.
    """
    from src.vectorstore.embedder import search_collection
    results = search_collection(query, config.COLLECTION_SRS, n_results=3)

    if not results:
        return "No relevant SRS documents found in knowledge base."

    lines = ["=== Relevant SRS Requirements ==="]
    for i, r in enumerate(results, 1):
        lines.append(format_single_result(r, i))
        lines.append("-" * 40)

    return "\n".join(lines)


def build_full_context(cr_text: str) -> Dict[str, str]:
    """
    Master function — builds ALL context sections at once.
    This is called right before sending to the LLM.

    cr_text: the new CR description the user pasted/uploaded

    Returns a dict with all context sections separately,
    so the prompt builder can arrange them however it needs.
    """
    logger.info("Building full context from knowledge base...")

    context = {
        "similar_crs":    build_cr_context(cr_text),
        "test_cases":     build_test_case_context(cr_text),
        "qa_issues":      build_qa_issues_context(cr_text),
        "srs_context":    build_srs_context(cr_text),
    }

    # Log how much context was found
    for key, value in context.items():
        line_count = value.count("\n")
        logger.info(f"Context '{key}': {line_count} lines")

    return context


def build_context_string(cr_text: str) -> str:
    """
    Builds one combined context string from all sources.
    Used when you want a single block of context for the prompt.
    """
    sections = build_full_context(cr_text)
    combined = "\n\n".join(sections.values())
    logger.info(f"Total context length: {len(combined)} characters")
    return combined


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    test_query = "loan repayment schedule calculation change"
    print("Building context for test query...")
    print(f"Query: {test_query}\n")

    context = build_full_context(test_query)
    for section, content in context.items():
        print(f"\n{'='*50}")
        print(f"SECTION: {section}")
        print(f"{'='*50}")
        print(content[:300])