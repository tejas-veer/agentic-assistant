from typing import Optional, List, Dict, Any
from pydantic import Field
from datetime import datetime
from ..shared.base_entity import AuditableEntity
from ..shared.enums import AssistantType, ConversationStatus


class AssistantSession(AuditableEntity):
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
    session_id: str
    role: str
    content: str
    audio_url: Optional[str] = None
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None


class AssistantIntent(AuditableEntity):
    name: str
    description: str
    examples: List[str] = Field(default_factory=list)
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class VoiceConfig(AuditableEntity):
    name: str
    provider: str
    voice_id: str
    language: str = "en-US"
    speed: float = 1.0
    pitch: float = 1.0
    is_default: bool = False


class AssistantContext(AuditableEntity):
    session_id: str
    current_intent: Optional[str] = None
    pending_items: List[Dict[str, Any]] = Field(default_factory=list)
    confirmed_items: List[Dict[str, Any]] = Field(default_factory=list)
    awaiting_confirmation: bool = False
    last_query: Optional[str] = None
    menu_context: Dict[str, Any] = Field(default_factory=dict)

