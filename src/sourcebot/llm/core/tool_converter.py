# sourcebot/llm/core/tool_converter.py

from sourcebot.llm.core.tool import Tool


def dict_to_tool(t: dict) -> Tool:
    fn = t["function"]

    return Tool(
        name=fn["name"],
        description=fn.get("description", ""),
        parameters=fn["parameters"],
    )


def normalize_tools(tools):
    if not tools:
        return []

    normalized = []

    for t in tools:
        if hasattr(t, "name"):
            normalized.append(t)
        elif isinstance(t, dict):
            normalized.append(dict_to_tool(t))
        else:
            raise TypeError(f"Unsupported tool type: {type(t)}")

    return normalized