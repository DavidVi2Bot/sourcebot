# sourcebot/llm/openai/converter.py

from sourcebot.llm.core.message import Message, ToolCall, ToolResult


def to_openai_messages(messages: list[Message]):
    result = []

    for msg in messages:
        if msg.role == "tool":
            # tool result
            for tr in msg.tool_results:
                result.append({
                    "role": "tool",
                    "tool_call_id": tr.tool_call_id,
                    "content": tr.content,
                })
            continue

        m = {
            "role": msg.role,
            "content": msg.content,
        }

        if msg.tool_calls:
            m["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]

        result.append(m)

    return result

def to_openai_tools(tools):
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            },
        }
        for t in tools
    ]