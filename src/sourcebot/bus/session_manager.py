# sourcebot/bus/session_manager.py
from datetime import datetime
from typing import Any, Dict

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get(self, session_key: str) -> Dict[str, Any]:
        if session_key not in self.sessions:
            self.sessions[session_key] = {
                "created_at": datetime.utcnow(),
                "state": {},
                "history": []
            }
        return self.sessions[session_key]

    def append_history(self, session_key: str, message: InboundMessage):
        session = self.get(session_key)
        session["history"].append(message)