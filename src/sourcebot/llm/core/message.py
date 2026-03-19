# sourcebot/llm/core/message.py

from typing import List, Optional, Any


class ToolCall:
    def __init__(self, id: str, name: str, arguments: Any):
        self.id = id
        self.name = name
        self.arguments = arguments


class ToolResult:
    def __init__(self, tool_call_id: str, content: str):
        self.tool_call_id = tool_call_id
        self.content = content


class Message:
    def __init__(
        self,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[List[ToolCall]] = None,
        tool_results: Optional[List[ToolResult]] = None,
        metadata: dict = None,
    ):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls or []
        self.tool_results = tool_results or []
        self.metadata = metadata or {}

    # Convert to dictionary (for storage)
    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "tool_results": [tr.to_dict() for tr in self.tool_results],
            "metadata": self.metadata,
        }

    # Restore from dict
    @staticmethod
    def from_dict(data: dict) -> "Message":
        return Message(
            role=data.get("role"),
            content=data.get("content"),
            tool_calls=[ToolCall.from_dict(tc) for tc in data.get("tool_calls", [])],
            tool_results=[ToolResult.from_dict(tr) for tr in data.get("tool_results", [])],
            metadata=data.get("metadata", {}),
        )