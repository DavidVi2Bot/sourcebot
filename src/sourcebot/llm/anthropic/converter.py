# sourcebot/llm/anthropic/converter.py
from sourcebot.llm.core.message import Message

def to_anthropic_messages(messages: list[Message]):
    system = None
    result = []
    for msg in messages:
        if msg.role == "system":
            system = msg.content
            continue
        if msg.role == "tool":
            # tool_result → user
            for tr in msg.tool_results:
                result.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tr.tool_call_id,
                            "content": tr.content,
                        }
                    ],
                })
            continue

        content_blocks = []

        if msg.content:
            content_blocks.append({
                "type": "text",
                "text": msg.content
            })

        # tool_call → tool_use
        for tc in msg.tool_calls:
            content_blocks.append({
                "type": "tool_use",
                "id": tc.id,
                "name": tc.name,
                "input": tc.arguments,
            })

        result.append({
            "role": msg.role,
            "content": content_blocks if content_blocks else ""
        })

    return system, result


def to_anthropic_tools(tools):
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.parameters,
        }
        for t in tools
    ]