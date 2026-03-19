# sourcebot/memory/window_policy.py
from sourcebot.llm.core.message import Message
class WindowMemoryPolicy:
    """
    A simple strategy based on window size:
    - Retain the most recent `memory_window` messages
    - Compress the rest
    """

    def select_messages(
        self,
        messages: list[Message],
        last_consolidated: int,
        memory_window: int,
        archive_all: bool,
    ):
        total = len(messages)

        if total <= last_consolidated:
            return [], last_consolidated

        if archive_all:
            old_messages = messages[last_consolidated:]
            return old_messages, total

        keep_from = max(total - memory_window, 0)

        start = last_consolidated
        end = min(keep_from, total)

        if start >= end:
            return [], last_consolidated

        old_messages = messages[start:end]

        return old_messages, end