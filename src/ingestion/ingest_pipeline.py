# src/ingestion/ingest_pipeline.py
# This is the master ingestion orchestrator.
# It connects pdf_loader → chroma_manager
# Run this whenever you add new PDFs to the knowledge base.

from pathlib import Path
from typing import Dict
from loguru import logger

import config
from src.ingestion.pdf_loader import load_all_pdfs_from_folder, build_documents
from src.vectorstore.chroma_manager import add_documents_to_vectorstore, get_collection_stats

# Maps each folder to its collection name and document type label
INGESTION_SOURCES = [
    {
        "folder": config.CR_PATH,
        "doc_type": "cr",
        "collection": config.COLLECTION_CRS,
        "label": "Change Requests"
    },
    {
        "folder": config.SRS_PATH,
        "doc_type": "srs",
        "collection": config.COLLECTION_SRS,
        "label": "SRS Documents"
    },
    {
        "folder": config.TEST_CASES_PATH,
        "doc_type": "test_case",
        "collection": config.COLLECTION_TEST_CASES,
        "label": "Test Cases"
    },
    {
        "folder": config.QA_ISSUES_PATH,
        "doc_type": "qa_issue",
        "collection": config.COLLECTION_QA_ISSUES,
        "label": "QA Issues"
    },
    {
        "folder": config.FEEDBACK_PATH,
        "doc_type": "feedback",
        "collection": config.COLLECTION_FEEDBACK,
        "label": "Feedback"
    },
]


def ingest_all() -> Dict[str, int]:
    """
    Scans ALL knowledge base folders and ingests any new PDFs.
    Skips files already ingested (duplicate detection via file hash).
    Returns a summary dict of how many chunks were added per collection.
    """
    logger.info("=" * 50)
    logger.info("Starting full knowledge base ingestion...")
    logger.info("=" * 50)

    summary = {}

    for source in INGESTION_SOURCES:
        logger.info(f"Processing: {source['label']}")
        docs = load_all_pdfs_from_folder(source["folder"], source["doc_type"])
        added = add_documents_to_vectorstore(docs, source["collection"])
        summary[source["label"]] = added

    logger.info("=" * 50)
    logger.info("Ingestion complete!")
    logger.info("=" * 50)
    return summary


def ingest_single_file(file_path: Path, doc_type: str, collection: str) -> int:
    """
    Ingest a single PDF file directly.
    Used by the UI when user uploads a file manually.

    file_path:  full path to the PDF
    doc_type:   one of "cr", "srs", "test_case", "qa_issue", "feedback"
    collection: ChromaDB collection name from config
    """
    logger.info(f"Ingesting single file: {file_path.name}")
    docs = build_documents(file_path, doc_type)
    added = add_documents_to_vectorstore(docs, collection)
    return added


def get_ingestion_stats() -> Dict[str, int]:
    """
    Returns how many chunks are stored per collection.
    Used in Dashboard and Knowledge Manager pages.
    """
    return get_collection_stats()


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    summary = ingest_all()

    print("\n📊 Ingestion Summary:")
    print("-" * 35)
    for label, count in summary.items():
        status = f"{count} chunks added" if count > 0 else "no new files"
        print(f"  {label:<20} → {status}")

    print("\n📦 Total in Knowledge Base:")
    print("-" * 35)
    stats = get_ingestion_stats()
    for name, count in stats.items():
        print(f"  {name:<25} → {count} chunks")