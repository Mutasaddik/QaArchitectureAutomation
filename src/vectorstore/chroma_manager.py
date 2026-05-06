# src/vectorstore/chroma_manager.py
# This file is responsible for:
# 1. Creating and managing ChromaDB client
# 2. Creating separate collections for each document type
# 3. Adding documents to collections
# 4. Checking for duplicates using file hash

from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from loguru import logger

import config


def get_embedding_function():
    """
    Returns the embedding model.
    This converts text into numbers (vectors) that ChromaDB stores.
    We use nomic-embed-text running locally via Ollama.
    """
    return OllamaEmbeddings(
        model=config.OLLAMA_EMBED_MODEL,
        base_url=config.OLLAMA_BASE_URL
    )


def get_chroma_client():
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DB_PATH)
    )

def get_vectorstore(collection_name: str) -> Chroma:
    embeddings = get_embedding_function()
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(config.CHROMA_DB_PATH)
    )
    return vectorstore


def get_all_ingested_hashes(collection_name: str) -> set:
    """
    Returns a set of all file hashes already stored in a collection.
    Used to detect duplicates — if a file hash exists, skip re-ingestion.
    """
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(collection_name)
        results = collection.get(include=["metadatas"])
        hashes = set()
        for metadata in results["metadatas"]:
            if metadata and "file_hash" in metadata:
                hashes.add(metadata["file_hash"])
        return hashes
    except Exception as e:
        logger.error(f"Error fetching hashes from {collection_name}: {e}")
        return set()


def add_documents_to_vectorstore(
        documents: List[Document],
        collection_name: str,
        skip_duplicates: bool = True
) -> int:
    """
    Adds a list of Document chunks into ChromaDB.

    - skip_duplicates: if True, checks file hash before adding
    - Returns count of how many chunks were actually added
    """
    if not documents:
        logger.warning("No documents to add.")
        return 0

    # ── Duplicate check ──────────────────────────────────────
    if skip_duplicates:
        existing_hashes = get_all_ingested_hashes(collection_name)
        # Filter out documents whose file_hash is already in ChromaDB
        new_documents = [
            doc for doc in documents
            if doc.metadata.get("file_hash") not in existing_hashes
        ]
        skipped = len(documents) - len(new_documents)
        if skipped > 0:
            logger.info(f"Skipped {skipped} chunks (already ingested)")
        documents = new_documents

    if not documents:
        logger.info("All documents already ingested. Nothing to add.")
        return 0

    # ── Add to ChromaDB ──────────────────────────────────────
    try:
        vectorstore = get_vectorstore(collection_name)
        vectorstore.add_documents(documents)
        logger.info(f"Added {len(documents)} chunks to '{collection_name}'")
        return len(documents)
    except Exception as e:
        logger.error(f"Failed to add documents to {collection_name}: {e}")
        return 0


def delete_collection(collection_name: str) -> bool:
    """
    Completely deletes a collection from ChromaDB.
    Used in Settings page to reset knowledge base.
    """
    try:
        client = get_chroma_client()
        client.delete_collection(collection_name)
        logger.info(f"Deleted collection: {collection_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete collection {collection_name}: {e}")
        return False


def get_collection_stats() -> dict:
    """
    Returns count of documents in each collection.
    Used in Dashboard page to show knowledge base statistics.
    """
    stats = {}
    collections = [
        config.COLLECTION_CRS,
        config.COLLECTION_SRS,
        config.COLLECTION_TEST_CASES,
        config.COLLECTION_QA_ISSUES,
        config.COLLECTION_FEEDBACK,
    ]
    client = get_chroma_client()
    for name in collections:
        try:
            col = client.get_or_create_collection(name)
            stats[name] = col.count()
        except Exception:
            stats[name] = 0
    return stats


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing ChromaDB connection...")
    stats = get_collection_stats()
    print("\nCollection stats:")
    for name, count in stats.items():
        print(f"  {name}: {count} chunks")
    print("\nChromaDB is working correctly!")