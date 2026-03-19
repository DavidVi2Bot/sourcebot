# sourcebot/llm/core/response.py

from typing import List, Optional, Dict, Any


class ToolCall:
    def __init__(self, id: str, name: str, arguments: Any):
        self.id = id
        self.name = name
        self.arguments = arguments


class LLMResponse:
    def __init__(
        self,
        content: Optional[str],
        tool_calls: Optional[List[ToolCall]] = None,
        finish_reason: Optional[str] = None,
        usage: Optional[Dict[str, int]] = None,
        raw = None,
    ):
        self.content = content
        self.tool_calls = tool_calls or []
        self.finish_reason = finish_reason
        self.usage = usage
        self.raw = raw

    @property
    def has_tool_calls(self):
        return len(self.tool_calls) > 0