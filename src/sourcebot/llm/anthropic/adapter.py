# sourcebot/llm/anthropic/adapter.py
from sourcebot.llm.core.adapter import BaseAdapter
from sourcebot.llm.core.response import LLMResponse, ToolCall


class AnthropicAdapter(BaseAdapter):

    def from_response(self, response) -> LLMResponse:
        text_parts = []
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)

            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )

        return LLMResponse(
            content="\n".join(text_parts) if text_parts else None,
            tool_calls=tool_calls,
            finish_reason=response.stop_reason,
            raw=response,
        )