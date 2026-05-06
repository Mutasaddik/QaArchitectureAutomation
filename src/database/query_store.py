# src/database/query_store.py
# A simple but powerful SQL query knowledge base.
# Queries are stored in a JSON file.
# Search works by keyword OR semantic meaning.

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger

import config

# ── Storage file path ────────────────────────────────────────
QUERY_FILE = config.KNOWLEDGE_BASE_PATH / "queries" / "query_repository.json"


# ── File Operations ──────────────────────────────────────────

def _load_all() -> List[Dict]:
    """Load all queries from JSON file."""
    try:
        data = json.loads(QUERY_FILE.read_text(encoding="utf-8"))
        return data.get("queries", [])
    except Exception as e:
        logger.error(f"Failed to load query file: {e}")
        return []


def _save_all(queries: List[Dict]):
    """Save all queries back to JSON file."""
    QUERY_FILE.write_text(
        json.dumps({"queries": queries}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# ── CRUD ─────────────────────────────────────────────────────

def add_query(
    title: str,
    sql: str,
    module: str,
    cr_id: str = "",
    tables: str = "",
    purpose: str = "",
    tags: List[str] = None
) -> Dict:
    """
    Add a new query to the repository.

    title:   short name  e.g. "Check weekly repayment records"
    sql:     the actual SQL query
    module:  e.g. "Loan", "Notification", "Report"
    cr_id:   optional CR reference e.g. "CR-2024-089"
    tables:  tables used e.g. "loan_repayments, installments"
    purpose: what this query validates
    tags:    list of keywords e.g. ["weekly", "loan", "repayment"]
    """
    queries = _load_all()

    entry = {
        "id":         str(uuid.uuid4())[:8],   # short unique ID
        "title":      title,
        "sql":        sql,
        "module":     module,
        "cr_id":      cr_id,
        "tables":     tables,
        "purpose":    purpose,
        "tags":       tags or [],
        "created_at": datetime.now().isoformat()
    }

    queries.append(entry)
    _save_all(queries)
    logger.info(f"Query added: '{title}' (ID: {entry['id']})")
    return entry


def get_all_queries() -> List[Dict]:
    """Return all saved queries."""
    return _load_all()


def delete_query(query_id: str) -> bool:
    """Delete a query by its ID."""
    queries = _load_all()
    original_count = len(queries)
    queries = [q for q in queries if q["id"] != query_id]
    if len(queries) < original_count:
        _save_all(queries)
        logger.info(f"Deleted query ID: {query_id}")
        return True
    return False


def get_all_modules() -> List[str]:
    """Return unique list of all modules in repository."""
    queries = _load_all()
    return sorted(set(q["module"] for q in queries if q.get("module")))


# ── Search ───────────────────────────────────────────────────

def keyword_search(keyword: str, module: str = None) -> List[Dict]:
    """
    Fast keyword search across title, purpose, tags, tables, sql.
    Optional module filter.

    Returns ranked results — more field matches = higher rank.
    """
    keyword_lower = keyword.lower()
    queries = _load_all()
    scored = []

    for q in queries:
        # Optional module filter
        if module and q.get("module", "").lower() != module.lower():
            continue

        score = 0
        # Each field match adds to score — title match is most valuable
        if keyword_lower in q.get("title",   "").lower(): score += 4
        if keyword_lower in q.get("purpose", "").lower(): score += 3
        if keyword_lower in " ".join(q.get("tags", [])).lower(): score += 3
        if keyword_lower in q.get("tables",  "").lower(): score += 2
        if keyword_lower in q.get("sql",     "").lower(): score += 1
        if keyword_lower in q.get("cr_id",   "").lower(): score += 2

        if score > 0:
            scored.append({**q, "_score": score})

    # Sort by score descending
    scored.sort(key=lambda x: x["_score"], reverse=True)
    logger.info(f"Keyword search '{keyword}': {len(scored)} results")
    return scored


def semantic_search(sentence: str, top_k: int = 5) -> List[Dict]:
    """
    Semantic search using ChromaDB embeddings.
    Finds queries by MEANING even if exact words don't match.

    e.g. "find borrower payment history" will match
         a query about "customer repayment records"
    """
    from src.vectorstore.chroma_manager import get_vectorstore
    import config as cfg

    QUERY_COLLECTION = "sql_queries"

    try:
        vectorstore = get_vectorstore(QUERY_COLLECTION)
        results = vectorstore.similarity_search(sentence, k=top_k)

        matched = []
        all_queries = _load_all()
        query_map = {q["id"]: q for q in all_queries}

        for doc in results:
            qid = doc.metadata.get("query_id")
            if qid and qid in query_map:
                matched.append(query_map[qid])

        logger.info(f"Semantic search '{sentence}': {len(matched)} results")
        return matched

    except Exception as e:
        logger.warning(f"Semantic search failed, falling back to keyword: {e}")
        return keyword_search(sentence)


def smart_search(input_text: str, module: str = None, top_k: int = 5) -> List[Dict]:
    """
    Combined search — tries semantic first, merges with keyword results.
    This is what the UI calls.

    Returns deduplicated, ranked list of matching queries.
    """
    semantic_results = semantic_search(input_text, top_k)
    keyword_results  = keyword_search(input_text, module)

    # Merge and deduplicate by ID
    seen_ids = set()
    merged   = []

    for q in semantic_results + keyword_results:
        qid = q.get("id")
        if qid not in seen_ids:
            seen_ids.add(qid)
            merged.append(q)

    return merged[:top_k]


def index_queries_to_chromadb():
    """
    Index all queries into ChromaDB for semantic search.
    Run this after adding new queries in bulk.
    The UI calls this automatically when a query is added.
    """
    from src.vectorstore.chroma_manager import get_vectorstore
    from langchain_core.documents import Document

    QUERY_COLLECTION = "sql_queries"
    queries = _load_all()

    if not queries:
        logger.warning("No queries to index.")
        return

    vectorstore = get_vectorstore(QUERY_COLLECTION)
    docs = []

    for q in queries:
        # Combine searchable text for embedding
        searchable_text = f"""
        Title: {q['title']}
        Module: {q['module']}
        Purpose: {q['purpose']}
        Tables: {q['tables']}
        Tags: {' '.join(q.get('tags', []))}
        SQL: {q['sql']}
        """.strip()

        docs.append(Document(
            page_content=searchable_text,
            metadata={"query_id": q["id"], "module": q["module"]}
        ))

    vectorstore.add_documents(docs)
    logger.info(f"Indexed {len(docs)} queries into ChromaDB.")


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing Query Repository...\n")

    # Add sample queries
    add_query(
        title="Check weekly repayment records",
        sql="SELECT * FROM loan_repayments WHERE frequency = 'weekly' ORDER BY created_at DESC;",
        module="Loan",
        cr_id="CR-2024-089",
        tables="loan_repayments",
        purpose="Validate weekly repayment records are created correctly",
        tags=["weekly", "repayment", "loan", "frequency"]
    )

    add_query(
        title="Check loan installment breakdown",
        sql="SELECT loan_id, installment_no, amount, due_date, status FROM installments WHERE loan_id = ? ORDER BY installment_no;",
        module="Loan",
        cr_id="CR-2024-089",
        tables="installments",
        purpose="Validate installment records and amounts after repayment schedule change",
        tags=["installment", "loan", "amount", "schedule"]
    )

    add_query(
        title="Check SMS notification sent for weekly payment",
        sql="SELECT * FROM notifications WHERE type = 'SMS' AND trigger_event = 'weekly_payment_due' ORDER BY sent_at DESC;",
        module="Notification",
        cr_id="CR-2024-089",
        tables="notifications",
        purpose="Verify SMS notifications are triggered for weekly payment due dates",
        tags=["sms", "notification", "weekly", "payment"]
    )

    print(f"Total queries stored: {len(get_all_queries())}")
    print(f"Modules available: {get_all_modules()}")

    print("\n--- Keyword Search: 'weekly loan' ---")
    results = keyword_search("weekly")
    for r in results:
        print(f"  [{r['id']}] {r['title']} | Module: {r['module']} | Score: {r.get('_score', 0)}")

    print("\n--- Indexing to ChromaDB for semantic search ---")
    index_queries_to_chromadb()

    print("\n--- Semantic Search: 'borrower payment schedule validation' ---")
    results = smart_search("borrower payment schedule validation")
    for r in results:
        print(f"  [{r['id']}] {r['title']} | Module: {r['module']}")