# src/feedback/feedback_manager.py
# Handles user feedback on generated test plans and test cases.
# When you rate output as bad and provide corrections,
# those corrections get saved and re-ingested into ChromaDB.
# This is how the system learns and improves over time.

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger

import config
from src.vectorstore.chroma_manager import get_vectorstore
from langchain_core.documents import Document


# ── Feedback storage file ────────────────────────────────────
FEEDBACK_FILE = config.KNOWLEDGE_BASE_PATH / "feedback" / "feedback_log.json"


def _load_feedback() -> List[Dict]:
    """Load all feedback from JSON file."""
    try:
        if not FEEDBACK_FILE.exists():
            return []
        return json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load feedback: {e}")
        return []


def _save_feedback(entries: List[Dict]):
    """Save all feedback to JSON file."""
    FEEDBACK_FILE.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def save_feedback(
    cr_text: str,
    generated_output: str,
    output_type: str,        # "test_plan" or "test_case"
    rating: int,             # 1-5 stars
    correction: str = "",    # what the correct output should look like
    comments: str = ""       # free text comments
) -> Dict:
    """
    Save feedback for a generated output.

    rating:     1 = very bad, 5 = perfect
    correction: if rating < 3, user provides the correct version
                this gets re-ingested into ChromaDB as knowledge
    """
    entries = _load_feedback()

    entry = {
        "id":               f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "cr_text":          cr_text[:500],   # truncate for storage
        "generated_output": generated_output[:1000],
        "output_type":      output_type,
        "rating":           rating,
        "correction":       correction,
        "comments":         comments,
        "created_at":       datetime.now().isoformat()
    }

    entries.append(entry)
    _save_feedback(entries)
    logger.info(f"Feedback saved: rating={rating}, type={output_type}")

    # ── If rating is low and correction provided, learn from it ──
    if rating <= 2 and correction.strip():
        _ingest_correction_to_chromadb(entry)

    return entry


def _ingest_correction_to_chromadb(feedback_entry: Dict):
    """
    When user provides a correction, store it in ChromaDB
    so future generations can learn from it.

    This is the "learning" mechanism of the system.
    """
    try:
        vectorstore = get_vectorstore(config.COLLECTION_FEEDBACK)

        # Build a document that captures what went wrong and what's correct
        content = f"""
FEEDBACK CORRECTION - {feedback_entry['output_type'].upper()}
CR Context: {feedback_entry['cr_text']}

What was generated (incorrect):
{feedback_entry['generated_output']}

What the correct output should be:
{feedback_entry['correction']}

Comments: {feedback_entry.get('comments', '')}
        """.strip()

        doc = Document(
            page_content=content,
            metadata={
                "doc_type":    "feedback",
                "output_type": feedback_entry["output_type"],
                "rating":      feedback_entry["rating"],
                "feedback_id": feedback_entry["id"],
                "created_at":  feedback_entry["created_at"]
            }
        )

        vectorstore.add_documents([doc])
        logger.info(f"Correction ingested to ChromaDB: {feedback_entry['id']}")

    except Exception as e:
        logger.error(f"Failed to ingest correction: {e}")


def get_all_feedback() -> List[Dict]:
    """Return all saved feedback entries."""
    return _load_feedback()


def get_feedback_stats() -> Dict:
    """
    Returns feedback statistics for the Dashboard.
    Average rating, total count, breakdown by type.
    """
    entries = _load_feedback()
    if not entries:
        return {
            "total":        0,
            "average":      0,
            "by_type":      {},
            "low_rated":    0,
            "high_rated":   0
        }

    total   = len(entries)
    avg     = sum(e["rating"] for e in entries) / total
    by_type = {}

    for e in entries:
        t = e["output_type"]
        if t not in by_type:
            by_type[t] = {"count": 0, "total_rating": 0}
        by_type[t]["count"]        += 1
        by_type[t]["total_rating"] += e["rating"]

    # Average per type
    for t in by_type:
        by_type[t]["average"] = round(
            by_type[t]["total_rating"] / by_type[t]["count"], 1
        )

    return {
        "total":      total,
        "average":    round(avg, 1),
        "by_type":    by_type,
        "low_rated":  sum(1 for e in entries if e["rating"] <= 2),
        "high_rated": sum(1 for e in entries if e["rating"] >= 4)
    }


def delete_feedback(feedback_id: str) -> bool:
    """Delete a feedback entry by ID."""
    entries  = _load_feedback()
    filtered = [e for e in entries if e["id"] != feedback_id]
    if len(filtered) < len(entries):
        _save_feedback(filtered)
        logger.info(f"Deleted feedback: {feedback_id}")
        return True
    return False


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing Feedback Manager...\n")

    # Save a good feedback
    save_feedback(
        cr_text          = "CR-2024-089: Weekly loan repayment support",
        generated_output = "Test Plan: Smoke, Sanity, Regression...",
        output_type      = "test_plan",
        rating           = 4,
        comments         = "Good coverage but missed SMS edge cases"
    )

    # Save a bad feedback with correction — this gets ingested to ChromaDB
    save_feedback(
        cr_text          = "CR-2024-089: Weekly loan repayment support",
        generated_output = "TC-001: Verify weekly option...",
        output_type      = "test_case",
        rating           = 2,
        correction       = "Test cases should follow folder/name/precondition format. Also need to include negative cases for invalid frequency values.",
        comments         = "Format was wrong, missing negative cases"
    )

    # Get stats
    stats = get_feedback_stats()
    print(f"Total feedback: {stats['total']}")
    print(f"Average rating: {stats['average']}/5")
    print(f"High rated (4-5): {stats['high_rated']}")
    print(f"Low rated (1-2):  {stats['low_rated']}")
    print(f"By type: {stats['by_type']}")
    print("\nFeedback manager working correctly!")