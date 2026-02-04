from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from app.infrastructure.database.connection import get_db_session
from app.infrastructure.database.repositories.business_repository import BusinessRepository, ResourceRepository
from app.api.v1.schemas import ApiResponse
from app.utils.null_check import Util
from app.domain.shared.enums import ResourceStatus

router = APIRouter(prefix="/businesses", tags=["Businesses"])


class ResourceStatusUpdate(BaseModel):
    status: ResourceStatus


def serialize_resource(resource) -> dict:
    return {
        "id": resource.id,
        "businessId": resource.business_id,
        "type": resource.type.value if resource.type else None,
        "name": resource.name,
        "capacity": resource.capacity,
        "metaJson": resource.meta_json,
        "status": resource.status.value if resource.status else None,
        "isActive": resource.is_active,
        "createdAt": resource.created_at.isoformat() if resource.created_at else None,
        "updatedAt": resource.updated_at.isoformat() if resource.updated_at else None,
    }


def serialize_business(business, include_resources: bool = False) -> dict:
    data = {
        "id": business.id,
        "name": business.name,
        "type": business.type.value if business.type else None,
        "intents": business.intents,
        "requiresApproval": business.requires_approval,
        "paymentFlow": business.payment_flow.value if business.payment_flow else None,
        "paymentModes": business.payment_modes,
        "resourceType": business.resource_type.value if business.resource_type else None,
        "contactPhone": business.contact_phone,
        "timings": business.timings,
        "isActive": business.is_active,
        "createdAt": business.created_at.isoformat() if business.created_at else None,
        "updatedAt": business.updated_at.isoformat() if business.updated_at else None,
    }
    if include_resources and hasattr(business, 'resources') and business.resources:
        data["resources"] = [serialize_resource(r) for r in business.resources if r.is_active]
    return data


@router.get("")
async def get_all_businesses(
    session: AsyncSession = Depends(get_db_session)
):
    repo = BusinessRepository(session)
    businesses = await repo.get_all()
    data = [serialize_business(b) for b in businesses]
    return ApiResponse(success=True, data=data)


@router.get("/{business_id}")
async def get_business(
    business_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    repo = BusinessRepository(session)
    business = await repo.get_with_resources(business_id)
    if Util.is_null(business):
        raise HTTPException(status_code=404, detail="Business not found")
    return ApiResponse(success=True, data=serialize_business(business, include_resources=True))


@router.get("/{business_id}/resources")
async def get_business_resources(
    business_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    repo = ResourceRepository(session)
    resources = await repo.get_by_business(business_id)
    data = [serialize_resource(r) for r in resources]
    return ApiResponse(success=True, data=data)


@router.get("/{business_id}/resources/available")
async def get_available_resources(
    business_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    repo = ResourceRepository(session)
    resources = await repo.get_available(business_id)
    data = [serialize_resource(r) for r in resources]
    return ApiResponse(success=True, data=data)


@router.post("/resources/{resource_id}/occupy")
async def occupy_resource(
    resource_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Mark a resource as occupied (customer is using it)"""
    repo = ResourceRepository(session)
    resource = await repo.get_by_id(resource_id)
    if Util.is_null(resource):
        raise HTTPException(status_code=404, detail="Resource not found")
    if resource.status != ResourceStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail=f"Resource is not available (current status: {resource.status.value})")
    
    updated = await repo.update_status(resource_id, ResourceStatus.OCCUPIED)
    return ApiResponse(success=True, data=serialize_resource(updated), message="Resource marked as occupied")


@router.post("/resources/{resource_id}/free")
async def free_resource(
    resource_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Mark a resource as available (free it up)"""
    repo = ResourceRepository(session)
    resource = await repo.get_by_id(resource_id)
    if Util.is_null(resource):
        raise HTTPException(status_code=404, detail="Resource not found")
    
    updated = await repo.update_status(resource_id, ResourceStatus.AVAILABLE)
    return ApiResponse(success=True, data=serialize_resource(updated), message="Resource is now available")


@router.patch("/resources/{resource_id}/status")
async def update_resource_status(
    resource_id: str,
    data: ResourceStatusUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update resource status (admin use)"""
    repo = ResourceRepository(session)
    resource = await repo.get_by_id(resource_id)
    if Util.is_null(resource):
        raise HTTPException(status_code=404, detail="Resource not found")
    
    updated = await repo.update_status(resource_id, data.status)
    return ApiResponse(success=True, data=serialize_resource(updated))
