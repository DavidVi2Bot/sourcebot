# sourcebot/llm/core/delta.py

class LLMDelta:
    def __init__(
        self,
        content: str = "",
        tool_call_delta: dict = None,
        finish_reason: str = None,
    ):
        self.content = content
        self.tool_call_delta = tool_call_delta
        self.finish_reason = finish_reason