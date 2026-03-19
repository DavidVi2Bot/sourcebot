# sourcebot/llm/openai/adapter.py

from sourcebot.llm.core.adapter import BaseAdapter
from sourcebot.llm.core.response import LLMResponse, ToolCall


class OpenAIAdapter(BaseAdapter):

    def from_response(self, response) -> LLMResponse:
        msg = response.choices[0].message

        tool_calls = []
        for tc in msg.tool_calls or []:
            tool_calls.append(
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=tc.function.arguments,
                )
            )

        return LLMResponse(
            content=msg.content,
            tool_calls=tool_calls,
            finish_reason=response.choices[0].finish_reason,
            raw=response,
        )