from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db_session
from app.services.assistant_service import AssistantService
from app.api.v1.schemas import AssistantSessionCreate, AssistantTextInput, ApiResponse

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


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
    return ApiResponse(success=True, data=assistant_session)


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

