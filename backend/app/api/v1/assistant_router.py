from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.infrastructure.database.connection import get_db_session
from app.services.assistant_service import AssistantService
from app.api.v1.schemas import AssistantSessionCreate, AssistantTextInput, ApiResponse
from app.utils.null_check import Util

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


def serialize_message(msg) -> dict:
    return {
        "id": msg.id,
        "sessionId": msg.session_id,
        "role": msg.role,
        "content": msg.content,
        "audioUrl": msg.audio_url,
        "intent": msg.intent,
        "entities": msg.entities,
        "confidence": float(msg.confidence) if msg.confidence else None,
        "createdAt": msg.created_at.isoformat() if msg.created_at else None,
    }


def serialize_session(sess) -> Optional[dict]:
    if Util.is_null(sess):
        return None
    data = {
        "id": sess.id,
        "sessionId": sess.session_id,
        "assistantType": sess.assistant_type.value if sess.assistant_type else None,
        "deviceId": sess.device_id,
        "phoneNumber": sess.phone_number,
        "status": sess.status.value if sess.status else None,
        "context": sess.context,
        "startedAt": sess.started_at.isoformat() if sess.started_at else None,
        "endedAt": sess.ended_at.isoformat() if sess.ended_at else None,
        "isActive": sess.is_active,
        "createdAt": sess.created_at.isoformat() if sess.created_at else None,
        "updatedAt": sess.updated_at.isoformat() if sess.updated_at else None,
    }
    if hasattr(sess, 'messages') and sess.messages:
        data["messages"] = [serialize_message(msg) for msg in sess.messages]
    return data


@router.post("/sessions")
async def create_session(
    data: AssistantSessionCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = AssistantService(session)
    assistant_session = await service.create_session(
        assistant_type=data.assistant_type,
        device_id=data.device_id,
        phone_number=data.phone_number
    )
    return ApiResponse(success=True, data=serialize_session(assistant_session))


@router.post("/text")
async def process_text(
    data: AssistantTextInput,
    session: AsyncSession = Depends(get_db_session)
):
    service = AssistantService(session)
    result = await service.process_text_input(
        session_id=data.session_id,
        text=data.text,
        device_id=data.device_id,
        business_id=data.business_id
    )
    return ApiResponse(success=True, data=result)


@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = AssistantService(session)
    await service.end_session(session_id)
    return ApiResponse(success=True, message="Session ended")
