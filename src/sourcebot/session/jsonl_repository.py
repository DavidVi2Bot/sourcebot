# sourcebot/session/jsonl_repository.py

import json
import shutil
from pathlib import Path
from typing import Any
from datetime import datetime

from sourcebot.session.session import Session
from sourcebot.session.repository import SessionRepository
from sourcebot.llm.core.message import Message


class JsonlSessionRepository(SessionRepository):

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.sessions_dir = self.workspace / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.legacy_sessions_dir = Path.home() / ".etherealbot" / "sessions"
        self._cache: dict[str, Session] = {}

    # -------------------------

    def _safe_filename(self, key: str) -> str:
        return key.replace(":", "_").replace("/", "_")

    def _get_session_path(self, key: str) -> Path:
        safe_key = self._safe_filename(key)
        return self.sessions_dir / f"{safe_key}.jsonl"

    def _get_legacy_session_path(self, key: str) -> Path:
        safe_key = self._safe_filename(key)
        return self.legacy_sessions_dir / f"{safe_key}.jsonl"

    # -------------------------

    def get_or_create(self, key: str) -> Session:
        if key in self._cache:
            return self._cache[key]

        session = self._load(key)
        if session is None:
            session = Session(key=key)

        self._cache[key] = session
        return session

    # -------------------------

    def _load(self, key: str) -> Session | None:
        path = self._get_session_path(key)

        if not path.exists():
            legacy = self._get_legacy_session_path(key)
            if legacy.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(legacy), str(path))

        if not path.exists():
            return None

        messages = []
        metadata: dict[str, Any] = {}
        created_at = None
        last_consolidated = 0

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)

                if data.get("_type") == "metadata":
                    metadata = data.get("metadata", {})
                    created_at = (
                        datetime.fromisoformat(data["created_at"])
                        if data.get("created_at")
                        else None
                    )
                    last_consolidated = data.get("last_consolidated", 0)
                else:
                    messages.append(Message.from_dict(data))

        return Session(
            key = key,
            messages = messages,
            created_at = created_at or datetime.now(),
            metadata = metadata,
            last_consolidated = last_consolidated,
        )

    # -------------------------

    def save(self, session: Session) -> None:
        path = self._get_session_path(session.key)

        with open(path, "w", encoding="utf-8") as f:
            metadata_line = {
                "_type": "metadata",
                "key": session.key,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "metadata": session.metadata,
                "last_consolidated": session.last_consolidated,
            }
            f.write(json.dumps(metadata_line, ensure_ascii=False) + "\n")

            for msg in session.messages:
                if hasattr(msg, "to_dict"):
                    data = msg.to_dict()
                else:
                    data = msg  # 兼容旧数据
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

        self._cache[session.key] = session

    # -------------------------

    def list_sessions(self) -> list[dict]:
        sessions = []

        for path in self.sessions_dir.glob("*.jsonl"):
            try:
                with open(path, encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line:
                        data = json.loads(first_line)
                        if data.get("_type") == "metadata":
                            sessions.append({
                                "key": data.get("key"),
                                "created_at": data.get("created_at"),
                                "updated_at": data.get("updated_at"),
                                "path": str(path),
                            })
            except Exception:
                continue

        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)