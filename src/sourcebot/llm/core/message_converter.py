# sourcebot/llm/core/message_converter.py
from sourcebot.llm.core.message import Message, ToolCall, ToolResult

def dict_to_message(msg: dict) -> Message:
    role = msg["role"]
    content = msg.get("content")

    tool_calls = []
    for tc in msg.get("tool_calls", []):
        tool_calls.append(
            ToolCall(
                id=tc["id"],
                name=tc["function"]["name"],
                arguments=tc["function"]["arguments"],
            )
        )

    tool_results = []
    if role == "tool":
        tool_results.append(
            ToolResult(
                tool_call_id=msg["tool_call_id"],
                content=content,
            )
        )

    return Message(
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_results=tool_results,
    )

