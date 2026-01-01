from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from app.models.db_models import ChatSession as DBChatSession


class MessageRole(str, Enum):
    """메시지 역할"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """메시지 DTO"""

    id: str
    session_id: str
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


# 기존 import 경로 호환을 위해 SQLAlchemy 모델을 재노출
ChatSession = DBChatSession
