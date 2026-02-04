from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.infrastructure.database.connection import get_db_session
from app.services.auth_service import AuthService, decode_token
from app.api.v1.schemas import ApiResponse
from app.domain.shared.enums import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None


class SigninRequest(BaseModel):
    email: EmailStr
    password: str


class AssignRoleRequest(BaseModel):
    business_id: str
    user_id: str
    role: UserRole


async def get_current_user_id(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload.get("sub")


@router.post("/signup")
async def signup(
    data: SignupRequest,
    session: AsyncSession = Depends(get_db_session)
):
    service = AuthService(session)
    try:
        result = await service.signup(
            name=data.name,
            email=data.email,
            password=data.password,
            phone=data.phone
        )
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signin")
async def signin(
    data: SigninRequest,
    session: AsyncSession = Depends(get_db_session)
):
    service = AuthService(session)
    try:
        result = await service.signin(
            email=data.email,
            password=data.password
        )
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session)
):
    service = AuthService(session)
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    memberships = await service.get_user_memberships(user_id)
    return ApiResponse(success=True, data={
        "user": user,
        "memberships": memberships
    })


@router.post("/assign-role")
async def assign_role(
    data: AssignRoleRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session)
):
    service = AuthService(session)
    try:
        result = await service.assign_role(
            assigner_user_id=user_id,
            business_id=data.business_id,
            target_user_id=data.user_id,
            role=data.role
        )
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/remove-role/{business_id}/{target_user_id}")
async def remove_role(
    business_id: str,
    target_user_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session)
):
    service = AuthService(session)
    try:
        await service.remove_role(
            assigner_user_id=user_id,
            business_id=business_id,
            target_user_id=target_user_id
        )
        return ApiResponse(success=True, message="Role removed")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/business/{business_id}/members")
async def get_business_members(
    business_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session)
):
    service = AuthService(session)
    members = await service.get_business_members(business_id)
    return ApiResponse(success=True, data=members)
