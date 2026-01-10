"""
Assistant Domain Models

Pydantic models for assistant-related entities.
"""

from typing import Optional, Dict, Any
from pydantic import Field
from datetime import datetime
from ..shared.base_entity import AuditableEntity
from ..shared.enums import AssistantType, ConversationStatus


class AssistantSession(AuditableEntity):
    """Represents an active assistant session."""
    session_id: str
    assistant_type: AssistantType
    device_id: Optional[str] = None
    phone_number: Optional[str] = None
    status: ConversationStatus = ConversationStatus.ACTIVE
    context: Dict[str, Any] = Field(default_factory=dict)
    order_id: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class ConversationMessage(AuditableEntity):
    """Represents a message in a conversation."""
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    audio_url: Optional[str] = None
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None
