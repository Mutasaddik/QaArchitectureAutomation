# src/vectorstore/embedder.py
# This file handles semantic search against ChromaDB.
# When you give it a query (e.g. a new CR description),
# it finds the most relevant chunks from the knowledge base.

from typing import List, Dict, Any, Optional
from loguru import logger

import config
from src.vectorstore.chroma_manager import get_vectorstore


def search_collection(
    query: str,
    collection_name: str,
    n_results: int = None,
    filter_metadata: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Search a single ChromaDB collection for chunks similar to the query.

    query:           the search text (e.g. new CR description)
    collection_name: which collection to search
    n_results:       how many results to return (default from config)
    filter_metadata: optional dict to filter by metadata fields
                     e.g. {"doc_type": "cr"} to only get CR chunks

    Returns a list of dicts with 'content' and 'metadata' keys.
    """
    if n_results is None:
        n_results = config.MAX_RETRIEVAL_RESULTS

    try:
        vectorstore = get_vectorstore(collection_name)

        # search_kwargs controls how many results come back
        search_kwargs = {"k": n_results}
        if filter_metadata:
            search_kwargs["filter"] = filter_metadata

        # similarity_search finds chunks closest in meaning to query
        results = vectorstore.similarity_search(
            query=query,
            **search_kwargs
        )

        # Convert LangChain Document objects to simple dicts
        formatted = []
        for doc in results:
            formatted.append({
                "content":  doc.page_content,
                "metadata": doc.metadata,
                "source":   doc.metadata.get("source", "unknown"),
                "doc_type": doc.metadata.get("doc_type", "unknown"),
            })

        logger.info(f"Found {len(formatted)} results in '{collection_name}'")
        return formatted

    except Exception as e:
        logger.error(f"Search failed in {collection_name}: {e}")
        return []


def search_all_collections(
    query: str,
    n_results_each: int = 3
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search ALL collections at once and return results grouped by type.
    This is used when generating a test plan — we want context from
    CRs, SRS, test cases, AND QA issues all at once.

    Returns a dict like:
    {
        "change_requests": [...],
        "srs_documents":   [...],
        "test_cases":      [...],
        "qa_issues":       [...],
        "feedback":        [...],
    }
    """
    collections = [
        config.COLLECTION_CRS,
        config.COLLECTION_SRS,
        config.COLLECTION_TEST_CASES,
        config.COLLECTION_QA_ISSUES,
        config.COLLECTION_FEEDBACK,
    ]

    all_results = {}
    for collection in collections:
        results = search_collection(query, collection, n_results_each)
        all_results[collection] = results

    total = sum(len(v) for v in all_results.values())
    logger.info(f"Total results across all collections: {total}")
    return all_results


def search_similar_crs(query: str, n_results: int = 3) -> List[Dict]:
    """Shortcut: search only past CRs."""
    return search_collection(query, config.COLLECTION_CRS, n_results)


def search_similar_test_cases(query: str, n_results: int = 5) -> List[Dict]:
    """Shortcut: search only existing test cases."""
    return search_collection(query, config.COLLECTION_TEST_CASES, n_results)


def search_qa_issues(query: str, n_results: int = 5) -> List[Dict]:
    """Shortcut: search only known QA environment issues."""
    return search_collection(query, config.COLLECTION_QA_ISSUES, n_results)


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing semantic search...")
    print("(Collections are empty — 0 results is correct for now)\n")

    results = search_all_collections("loan repayment calculation")

    for collection, hits in results.items():
        print(f"{collection}: {len(hits)} results")