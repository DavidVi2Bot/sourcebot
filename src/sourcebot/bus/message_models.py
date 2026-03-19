# sourcebot/bus/message_models.py
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass
class InboundMessage:
    channel: str
    sender_id: str
    conversation_id: str
    content: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    type: str = "text"

    @property
    def session_key(self) -> str:
        return f"{self.channel}:{self.conversation_id}:{self.sender_id}"


@dataclass
class OutboundMessage:
    channel: str
    conversation_id: str
    content: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    type: str = "text"
