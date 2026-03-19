# sourcebot/memory/llm_consolidator.py

import logging
logger = logging.getLogger(__name__)
from sourcebot.llm.core.message import Message
class LLMConsolidator:
    def __init__(
        self,
        llm
        ):
        self.llm = llm

    async def consolidate(self, current_memory: str, lines: list[str]):
        """
        Returns:
            (history_entry, updated_memory)
            or None if skipped
        """

        if not lines:
            return None

        conversation_chunk = "\n".join(lines)

        prompt = f"""
You are a memory consolidation engine.

Current long-term memory:
-------------------------
{current_memory}

New conversation chunk:
-------------------------
{conversation_chunk}

Task:
1. Extract important facts, preferences, decisions, architecture insights.
2. Merge them into long-term memory.
3. Avoid duplication.
4. Return TWO SECTIONS:

=== HISTORY_ENTRY ===
Short 1-2 paragraph summary of what happened.

=== UPDATED_MEMORY ===
Full updated long-term memory document.
"""
        response = await self.conversation_summary(prompt)

        if "=== HISTORY_ENTRY ===" not in response:
            logger.warning("Consolidation format invalid.")
            return None

        try:
            history = response.split("=== HISTORY_ENTRY ===")[1] \
                              .split("=== UPDATED_MEMORY ===")[0] \
                              .strip()

            updated = response.split("=== UPDATED_MEMORY ===")[1].strip()

            return history, updated

        except Exception:
            logger.exception("Failed to parse consolidation result.")
            return None

    async def conversation_summary(
        self, 
        prompt: str, 
        ) -> str:
        messages = [
            Message(role = "system", content = "You are a memory consolidation engine."),
            Message(role = "user", content = prompt),
        ]
        response = await self.llm.complete(
            messages,
            tools = None, 
        )
        return response.content