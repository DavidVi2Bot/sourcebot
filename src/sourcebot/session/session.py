# sourcebot/session/session.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from sourcebot.llm.core.message import Message

@dataclass
class Session:
    key: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    last_consolidated: int = 0

    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        msg = Message(
            role = role,
            content = content,
            metadata = kwargs
        )
        self.messages.append(msg)
        self.updated_at = datetime.now()
    
    def get_history(self, max_messages: int = 500):
        out = []
        for m in self.messages[-max_messages:]:
            entry = {
                "role": m.role,
                "content": m.content or "",
            }
            if m.tool_calls:
                entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": tc.arguments,
                        },
                    }
                    for tc in m.tool_calls
                ]
            if m.tool_results:
                entry["tool_call_id"] = m.tool_results[0].tool_call_id
            out.append(entry)
        return out

    def clear(self) -> None:
        """Clear all messages and reset the session to its initial state."""
        self.messages = []
        self.last_consolidated = 0
        self.updated_at = datetime.now()