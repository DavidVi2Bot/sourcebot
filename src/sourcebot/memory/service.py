# sourcebot/memory/service.py
import logging

logger = logging.getLogger(__name__)


class MemoryService:

    def __init__(self, store, policy, consolidator):
        self.store = store
        self.policy = policy
        self.consolidator = consolidator

        self._consolidating: set[str] = set()


    async def maybe_consolidate(
        self,
        session,
        memory_window: int = 50,
    ):
        """
        Decide whether consolidation should run.
        """

        if len(session.messages) <= memory_window:
            return

        if session.key in self._consolidating:
            return

        self._consolidating.add(session.key)

        async def _task():
            try:
                await self.consolidate(session, memory_window)
            finally:
                self._consolidating.discard(session.key)


        await _task()


    # The actual compression logic is executed.

    async def consolidate(
        self,
        session,
        memory_window = 50,
        archive_all = True,
    ):

        old_messages, new_last = self.policy.select_messages(
            session.messages,
            session.last_consolidated,
            memory_window,
            archive_all,
        )
        if not old_messages:
            return

        lines = []
        for m in old_messages:
            if not m.content:
                continue

            tools_used = m.metadata.get("tools_used", [])

            tools = (
                f" [tools: {', '.join(tools_used)}]"
                if tools_used
                else ""
            )

            ts = m.metadata.get("timestamp", "?")

            lines.append(
                f"[{ts[:16]}] "
                f"{m.role.upper()}{tools}: {m.content}"
            )

        current_memory = self.store.read_long_term()

        result = await self.consolidator.consolidate(
            current_memory, 
            lines, 
        )
        if not result:
            logger.warning("Memory consolidation skipped.")
            return

        history_entry, memory_update = result
        self.store.append_history(history_entry)

        if memory_update != current_memory:
            self.store.write_long_term(memory_update)
        session.last_consolidated = new_last



    # /new Dedicated mandatory archiving
    async def consolidate_archived(
        self,
        session_key: str,
        archived_messages: list[dict],
    ):
        """
        Used by /new command to archive everything.
        """
        from sourcebot.session import Session
        temp = Session(key = session_key)
        temp.messages = archived_messages
        await self.consolidate(
            temp,
            archive_all = True,
        )