from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class BaseEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AuditableEntity(BaseEntity):
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_active: bool = True

