# src/ingestion/pdf_loader.py

import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

import pdfplumber
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

import config


def compute_file_hash(file_path: Path) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def extract_text_from_pdf(file_path: Path) -> List[Dict[str, Any]]:
    pages = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text and len(text.strip()) > 20:
                    pages.append({
                        "page_number": page_num,
                        "text": text.strip()
                    })
        logger.info(f"Extracted {len(pages)} pages from {file_path.name}")
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path.name}: {e}")
    return pages


def build_documents(file_path: Path, doc_type: str) -> List[Document]:
    pages = extract_text_from_pdf(file_path)
    if not pages:
        logger.warning(f"No extractable text found in {file_path.name}")
        return []

    full_text = "\n\n".join(
        f"[Page {p['page_number']}]\n{p['text']}" for p in pages
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(full_text)

    file_hash = compute_file_hash(file_path)
    base_metadata = {
        "source":      file_path.name,
        "doc_type":    doc_type,
        "file_path":   str(file_path),
        "file_hash":   file_hash,
        "ingested_at": datetime.now().isoformat(),
        "total_pages": len(pages),
    }

    documents = []
    for i, chunk_text in enumerate(chunks):
        # Skip empty or page-break-only chunks
        clean = chunk_text.strip()
        if len(clean) < 50:
            continue
        metadata = {**base_metadata, "chunk_index": i, "total_chunks": len(chunks)}
        documents.append(Document(page_content=chunk_text, metadata=metadata))

    logger.info(f"Built {len(documents)} chunks from {file_path.name}")
    return documents


def load_all_pdfs_from_folder(folder_path: Path, doc_type: str) -> List[Document]:
    all_documents = []
    pdf_files = list(folder_path.glob("*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in {folder_path}")
        return []

    logger.info(f"Found {len(pdf_files)} PDF(s) in {folder_path}")

    for pdf_file in pdf_files:
        docs = build_documents(pdf_file, doc_type)
        all_documents.extend(docs)

    logger.info(f"Total chunks loaded from {folder_path.name}: {len(all_documents)}")
    return all_documents


if __name__ == "__main__":
    test_folder = config.CR_PATH
    docs = load_all_pdfs_from_folder(test_folder, "cr")
    print(f"\nTotal documents loaded: {len(docs)}")
    if docs:
        print(f"\nFirst chunk preview:\n{docs[0].page_content[:300]}")
        print(f"\nMetadata: {docs[0].metadata}")