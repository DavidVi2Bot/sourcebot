# sourcebot/session/repository.py

from abc import ABC, abstractmethod
from sourcebot.session.session import Session


class SessionRepository(ABC):

    @abstractmethod
    def get_or_create(self, key: str) -> Session:
        pass

    @abstractmethod
    def save(self, session: Session) -> None:
        pass

    @abstractmethod
    def list_sessions(self) -> list[dict]:
        pass