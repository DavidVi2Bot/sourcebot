# domain/context/message_builder.py
from pathlib import Path
from typing import Any, List, Optional, Dict
import base64
import mimetypes
from sourcebot.context import ContextBuilder
from sourcebot.llm.core.message import Message, ToolCall, ToolResult
from sourcebot.llm.core.message_converter import dict_to_message

import logging
logger = logging.getLogger(__name__)

class MessageBuilder:
    """Build messages for LLM including system, user, and tool messages."""

    def __init__(self, context_builder: ContextBuilder):
        self.context_builder = context_builder

    def _build_user_content(
        self,
        text: str,
        media: Optional[List[str]] = None
    ) -> Message:

        metadata: Dict[str, Any] = {}
        media_list: List[Dict[str, Any]] = []

        if media:
            for path_str in media:
                p = Path(path_str)
                mime, _ = mimetypes.guess_type(str(p))

                if not p.is_file() or not mime or not mime.startswith("image/"):
                    logger.warning(f"Skipping invalid media: {path_str}")
                    continue

                b64 = base64.b64encode(p.read_bytes()).decode()

                media_list.append({
                    "filename": p.name,
                    "mime": mime,
                    "base64": b64
                })

        if media_list:
            metadata["media"] = media_list

        return Message(
            role = "user",
            content = text,
            metadata = metadata,
        )

    def build_chat_messages(
        self,
        current_message: str,
        history: List[Any] = None,
        skill_names: Optional[List[str]] = None,
        media: Optional[List[str]] = None,
        channel: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> List[Message]:

        messages: List[Message] = []

        chat_prompt = self.context_builder.build_chat_prompt()
        if channel and conversation_id:
            chat_prompt += f"\n\n## Current Session\nChannel: {channel}\nConversation ID: {conversation_id}"

        messages.append(Message(role="system", content=chat_prompt))

        if history:
            for msg in history:
                if isinstance(msg, Message):
                    messages.append(msg)
                else:
                    messages.append(dict_to_message(msg))  

        user_content = self._build_user_content(current_message, media)

        messages.append(
            Message(
                role = user_content.role,
                content = user_content.content,  
            )
        )

        return messages
    
        # skills + rules 
        def build_messages(
            self,
            current_message: str,
            history: List[Dict[str, Any]] = None,
            skill_names: Optional[List[str]] = None,
            media: Optional[List[str]] = None,
            channel: Optional[str] = None,
            conversation_id: Optional[str] = None,
        ) -> List[Dict[str, Any]]:
            messages: List[Message] = []

            system_prompt = self.context_builder.build_system_prompt(skill_names)

            if channel and conversation_id:
                system_prompt += f"\n\n## Current Session\nChannel: {channel}\nConversation ID: {conversation_id}"

            messages.append(Message(role="system", content=system_prompt))

            user_content = self._build_user_content(current_message, media)

            messages.append(
                Message(
                    role = "user",
                    content = user_content["content"],
                )
            )

            return messages

    def add_tool_result(
        self,
        messages: List[Message],
        tool_call_id: str,
        result: str
    ) -> List[Message]:

        messages.append(
            Message(
                role="tool",
                tool_results=[
                    ToolResult(
                        tool_call_id=tool_call_id,
                        content=result
                    )
                ],
            )
        )

        return messages
    def add_assistant_message(
        self,
        messages,
        content=None,
        tool_calls=None,
    ):

        msg = Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls or [],
        )

        messages.append(msg)
        return messages