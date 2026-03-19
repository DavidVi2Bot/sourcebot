# sourcebot/conversation/service.py

import asyncio
from typing import Callable, Awaitable
import logging
from sourcebot.session.session import Session
from sourcebot.session.service import SessionService
from sourcebot.memory.service import MemoryService
from sourcebot.runtime.agent import Agent
from sourcebot.bus import InboundMessage, OutboundMessage

logger = logging.getLogger(__name__)

class ConversationService:
    """
    Orchestrates a full user conversation turn.

    Responsibilities:
    - Command routing
    - Session load/save
    - Context building
    - Agent execution
    - Memory consolidation scheduling
    """

    def __init__(
        self,
        session_service: SessionService,
        memory_service: MemoryService,
        agent: Agent,
        message_builder,
        bus = None,
        memory_window: int = 50,
    ):
        self.session_service = session_service
        self.memory_service = memory_service
        self.agent = agent
        self.message_builder = message_builder
        # self.bus = bus
        self.memory_window = memory_window

        self._consolidating: set[str] = set()

    
    # Entry point
    async def handle_message(
        self,
        msg: InboundMessage,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> OutboundMessage | None:

        if self._is_command(msg):
            return await self._handle_command(msg)

        if msg.channel == "system":
            return await self._handle_system_message(msg)
        return await self._handle_conversation(msg, on_progress)


    # Conversation flow
    async def _handle_conversation(
        self,
        msg: InboundMessage,
        on_progress: Callable[[str], Awaitable[None]] | None,
    ) -> OutboundMessage | None:
        # Session service
        session = self.session_service.get_history(msg.session_key)
        await self._maybe_schedule_consolidation(session)
        messages = self.message_builder.build_chat_messages(
            history = session.get_history(max_messages=self.memory_window),
            current_message = msg.content,
            media = msg.metadata if msg.metadata else None,
            channel = msg.channel,
            conversation_id = msg.conversation_id,
        )
        async def _bus_progress(content: str):
            if not self.bus:
                return
            metadata = dict(msg.metadata or {})
            metadata["_progress"] = True
            await self.bus.publish_outbound(
                OutboundMessage(
                    channel = msg.channel,
                    conversation_id = msg.conversation_id,
                    content = content,
                    metadata = data,
                )
            )
        final_content, _, tools_used = await self.agent.run(messages)

        if final_content is None:
            final_content = "I've completed processing but have no response."

        self.session_service.append_turn(
            session.key,
            user = msg.content,
            assistant = final_content,
            tools_used = tools_used,
        )
        return OutboundMessage(
            channel = msg.channel,
            conversation_id = msg.conversation_id,
            content = final_content,
            metadata = msg.metadata or {},
        )


    # System message
    async def _handle_system_message(
        self,
        msg: InboundMessage,
    ) -> OutboundMessage:

        key = msg.session_key
        session = self.session_service.get(key)

        messages = self.message_builder.build_messages(
            history = session.get_history(max_messages = self.memory_window),
            current_message = msg.content,
            channel = msg.channel,
            conversation_id = msg.conversation_id,
        )

        final_content, _ = await self.agent.run(messages)

        session.add_message("user", f"[System: {msg.sender_id}] {msg.content}")
        session.add_message("assistant", final_content)

        self.session_service.save(session)

        return OutboundMessage(
            channel = msg.channel,
            conversation_id = msg.conversation_id,
            content = final_content or "Background task completed.",
        )


    # commands
    def _is_command(self, msg: InboundMessage) -> bool:
        return msg.content.strip().startswith("/")

    async def _handle_command(self, msg: InboundMessage) -> OutboundMessage:

        cmd = msg.content.strip().lower()
        session = self.session_service.get_history(msg.session_key)

        if cmd == "/new":
            archived = session.messages.copy()
            session.clear()
            self.session_service.save(session)
            await self.memory_service.consolidate_archived(
                session.key, 
                archived
            )
            return OutboundMessage(
                channel = msg.channel,
                conversation_id = msg.conversation_id,
                content = "New session started. Memory consolidation in progress.",
            )

        if cmd == "/help":
            return OutboundMessage(
                channel = msg.channel,
                conversation_id = msg.conversation_id,
                content = (
                    "Available commands:\n"
                    "/new — Start a new conversation\n"
                    "/help — Show help"
                ),
            )
        return OutboundMessage(
            channel = msg.channel,
            conversation_id = msg.conversation_id,
            content = "Unknown command.",
        )

    # Memory consolidation
    async def _maybe_schedule_consolidation(self, session: Session):
        if (
            len(session.messages) <= self.memory_window
            or session.key in self._consolidating
        ):
            return
        self._consolidating.add(session.key)

        async def _task():
            try:
                await self.memory_service.maybe_consolidate(session)
            finally:
                self._consolidating.discard(session.key)
        await _task()