# sourcebot/session/service.py

from sourcebot.session.repository import SessionRepository
from typing import Any
class SessionService:

    def __init__(self, repo: SessionRepository):
        self.repo = repo

    def append_user_message(self, key: str, content: str):
        session = self.repo.get_or_create(key)
        session.add_message("user", content)
        self.repo.save(session)

    def append_assistant_message(self, key: str, content: str, **kwargs: Any | None):
        session = self.repo.get_or_create(key)
        session.add_message("assistant", content, **kwargs)
        self.repo.save(session)
    # Session
    def get_history(self, key: str):
        session = self.repo.get_or_create(key)
        return session

    def list_sessions(self):
        return self.repo.list_sessions()

    def append_turn(
        self,
        key: str,
        user: str,
        assistant: str,
        tools_used=None,
    ):
        session = self.repo.get_or_create(key)
        session.add_message("user", user)
        session.add_message("assistant", assistant, tools_used = tools_used)
        self.repo.save(session)

    def save(self, session: Any) -> None:
        
        return self.repo.save(session)


    