# src/session_manager.py
# Saves and restores complete session state across restarts.
# Every important action saves state to a JSON file.
# On app start, state is automatically restored.

import json
from pathlib import Path
from datetime import datetime
from loguru import logger

SESSION_FILE = Path("knowledge_base/feedback/session_state.json")
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)


def save_session(state: dict):
    """Save current session state to disk."""
    try:
        state["saved_at"] = datetime.now().isoformat()
        SESSION_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        logger.error(f"Failed to save session: {e}")


def load_session() -> dict:
    """Load last session state from disk."""
    try:
        if SESSION_FILE.exists():
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            logger.info(f"Session restored from {data.get('saved_at','unknown')}")
            return data
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
    return {}


def clear_session():
    """Clear saved session."""
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
            logger.info("Session cleared")
    except Exception as e:
        logger.error(f"Failed to clear session: {e}")


def get_session_info() -> dict:
    """Get basic info about saved session without loading everything."""
    try:
        if SESSION_FILE.exists():
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            return {
                "exists":   True,
                "saved_at": data.get("saved_at", "unknown"),
                "has_chat": bool(data.get("chat_history")),
                "has_cr":   bool(data.get("chat_cr_text")),
                "has_tp":   bool(data.get("tp_result")),
                "has_tc":   bool(data.get("tc_result")),
            }
    except:
        pass
    return {"exists": False}