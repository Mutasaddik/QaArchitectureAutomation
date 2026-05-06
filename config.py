# config.py
# This file is the single source of truth for all settings.
# Every other file imports from here — nothing is hardcoded elsewhere.

import os
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file so all os.getenv() calls work
load_dotenv()

# ── Base Paths ──────────────────────────────────────────────
# Path(__file__) = location of this config.py file
# .parent = the folder containing it (qa_assistant/)
BASE_DIR = Path(__file__).parent

# ── Knowledge Base Paths ─────────────────────────────────────
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base"
CR_PATH             = KNOWLEDGE_BASE_PATH / "crs"
SRS_PATH            = KNOWLEDGE_BASE_PATH / "srs"
TEST_CASES_PATH     = KNOWLEDGE_BASE_PATH / "test_cases"
QA_ISSUES_PATH      = KNOWLEDGE_BASE_PATH / "qa_issues"
FEEDBACK_PATH       = KNOWLEDGE_BASE_PATH / "feedback"

# ── Database Paths ───────────────────────────────────────────
CHROMA_DB_PATH = BASE_DIR / "chroma_db"
SQLITE_DB_PATH = BASE_DIR / "qa_assistant.db"

# ── Output Paths ─────────────────────────────────────────────
EXPORTS_PATH = BASE_DIR / "exports"
LOGS_PATH    = BASE_DIR / "logs"

# ── Ollama LLM Settings ──────────────────────────────────────
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL  = os.getenv("OLLAMA_LLM_MODEL", "llama3")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# LLM generation settings
LLM_TEMPERATURE = 0.2   # Low = more focused/deterministic output (good for test plans)
LLM_MAX_TOKENS  = 4096  # Max length of generated response

# ── ChromaDB Collection Names ────────────────────────────────
# Each type of document gets its own collection (like a table in SQL)
COLLECTION_CRS         = "change_requests"
COLLECTION_SRS         = "srs_documents"
COLLECTION_TEST_CASES  = "test_cases"
COLLECTION_QA_ISSUES   = "qa_issues"
COLLECTION_FEEDBACK    = "feedback"

# ── RAG (Retrieval) Settings ─────────────────────────────────
CHUNK_SIZE            = int(os.getenv("CHUNK_SIZE", 1000))   # Characters per chunk
CHUNK_OVERLAP         = int(os.getenv("CHUNK_OVERLAP", 200)) # Overlap between chunks
MAX_RETRIEVAL_RESULTS = int(os.getenv("MAX_RETRIEVAL_RESULTS", 5)) # How many chunks to retrieve

# ── App Settings ─────────────────────────────────────────────
APP_NAME    = os.getenv("APP_NAME", "QA Assistant")
APP_VERSION = "1.0.0"
APP_ICON    = "🧪"

# ── Auto-create all directories on import ───────────────────
# This ensures folders exist even on fresh setup
for path in [
    CR_PATH, SRS_PATH, TEST_CASES_PATH,
    QA_ISSUES_PATH, FEEDBACK_PATH,
    CHROMA_DB_PATH, EXPORTS_PATH, LOGS_PATH
]:
    path.mkdir(parents=True, exist_ok=True)
