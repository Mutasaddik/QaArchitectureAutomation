from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger


import config
from src.retrieval.context_builder import build_context_string
from src.generation.prompts import QA_SYSTEM_PROMPT, build_chat_prompt
from src.generation.llm_client import generate


class ChatSession:
    def __init__(self, session_id: str = None, cr_text: str = ""):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.cr_text    = cr_text
        self.history: List[Dict] = []
        self.created_at = datetime.now().isoformat()

    def add_message(self, role: str, content: str):
        self.history.append({
            "role":      role,
            "content":   content,
            "timestamp": datetime.now().isoformat()
        })

    def get_history_string(self) -> str:
        recent = self.history[-10:]
        lines  = []
        for msg in recent:
            role = "QA Engineer" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines) if lines else "No previous messages."

    def clear_history(self):
        self.history = []
        logger.info(f"Session {self.session_id} history cleared.")

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "cr_text":    self.cr_text,
            "history":    self.history,
            "created_at": self.created_at,
        }


class ChatEngine:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}

    def create_session(self, cr_text: str = "") -> ChatSession:
        session = ChatSession(cr_text=cr_text)
        self.sessions[session.session_id] = session
        logger.info(f"New chat session created: {session.session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.sessions.get(session_id)

    def get_or_create_session(self, session_id: str, cr_text: str = "") -> ChatSession:
        if session_id in self.sessions:
            return self.sessions[session_id]
        return self.create_session(cr_text)

    def chat(self, user_message: str, session: ChatSession, stream: bool = False) -> str:
        logger.info(f"Chat message in session {session.session_id}")
        session.add_message("user", user_message)

        # Always search ChromaDB with the user message
        # If no CR context set, search using just the message
        search_query = user_message
        if session.cr_text:
            search_query = f"{session.cr_text[:200]} {user_message}"

        kb_context = build_context_string(search_query)
        cr_context = session.cr_text if session.cr_text else "No specific CR provided. Answer based on knowledge base."

        prompt = build_chat_prompt(
            cr_context    = cr_context,
            kb_context    = kb_context,
            chat_history  = session.get_history_string(),
            user_question = user_message
        )

        response = generate(
            prompt        = prompt,
            system_prompt = QA_SYSTEM_PROMPT,
            temperature   = 0.3,
            stream        = stream
        )

        session.add_message("assistant", response)
        logger.info(f"Response generated ({len(response)} chars)")
        return response

    def list_sessions(self) -> List[Dict]:
        return [
            {
                "session_id":    s.session_id,
                "message_count": len(s.history),
                "created_at":    s.created_at,
                "cr_preview":    s.cr_text[:80] + "..." if len(s.cr_text) > 80 else s.cr_text
            }
            for s in self.sessions.values()
        ]


chat_engine = ChatEngine()


if __name__ == "__main__":
    sample_cr = "CR-2024-089: Weekly Loan Repayment Support"
    session   = chat_engine.create_session(cr_text=sample_cr)
    print(f"Session: {session.session_id}")
    response  = chat_engine.chat("What modules are impacted?", session, stream=True)
    print(f"\nMessages: {len(session.history)}")