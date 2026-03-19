# sourcebot/llm/core/tool_delta_aggregator.py

class ToolCallAggregator:

    def __init__(self):
        self.calls = {}

    def apply_delta(self, delta_tool_calls):
        """
        delta_tool_calls: OpenAI chunk delta.tool_calls
        """

        for tc in delta_tool_calls:
            idx = tc.index

            if idx not in self.calls:
                self.calls[idx] = {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": "",
                }

            if tc.function.arguments:
                self.calls[idx]["arguments"] += tc.function.arguments

    def build(self):
        from sourcebot.llm.core.message import ToolCall

        result = []
        for c in self.calls.values():
            result.append(
                ToolCall(
                    id=c["id"],
                    name=c["name"],
                    arguments=c["arguments"],
                )
            )
        return result