from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .base_repository import BaseRepository
from ..models import BusinessModel, ResourceModel, TeamMemberModel, FAQModel
from app.domain.shared.enums import ResourceStatus


class BusinessRepository(BaseRepository[BusinessModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BusinessModel)

    async def get_by_name(self, name: str) -> Optional[BusinessModel]:
        result = await self.session.execute(
            select(BusinessModel)
            .where(BusinessModel.name == name, BusinessModel.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_with_resources(self, business_id: str) -> Optional[BusinessModel]:
        result = await self.session.execute(
            select(BusinessModel)
            .where(BusinessModel.id == business_id, BusinessModel.is_active == True)
            .options(selectinload(BusinessModel.resources))
        )
        return result.scalar_one_or_none()


class ResourceRepository(BaseRepository[ResourceModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ResourceModel)

    async def get_by_business(self, business_id: str) -> List[ResourceModel]:
        result = await self.session.execute(
            select(ResourceModel)
            .where(ResourceModel.business_id == business_id, ResourceModel.is_active == True)
            .order_by(ResourceModel.name)
        )
        return list(result.scalars().all())

    async def get_available(self, business_id: str) -> List[ResourceModel]:
        result = await self.session.execute(
            select(ResourceModel)
            .where(
                ResourceModel.business_id == business_id,
                ResourceModel.status == ResourceStatus.AVAILABLE,
                ResourceModel.is_active == True
            )
            .order_by(ResourceModel.name)
        )
        return list(result.scalars().all())

    async def update_status(self, resource_id: str, status: ResourceStatus) -> Optional[ResourceModel]:
        return await self.update(resource_id, {"status": status})


class TeamMemberRepository(BaseRepository[TeamMemberModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TeamMemberModel)

    async def get_by_business(self, business_id: str) -> List[TeamMemberModel]:
        result = await self.session.execute(
            select(TeamMemberModel)
            .where(TeamMemberModel.business_id == business_id, TeamMemberModel.is_active == True)
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: str) -> List[TeamMemberModel]:
        result = await self.session.execute(
            select(TeamMemberModel)
            .where(TeamMemberModel.user_id == user_id, TeamMemberModel.is_active == True)
        )
        return list(result.scalars().all())

    async def get_by_business_and_user(self, business_id: str, user_id: str) -> Optional[TeamMemberModel]:
        result = await self.session.execute(
            select(TeamMemberModel)
            .where(
                TeamMemberModel.business_id == business_id,
                TeamMemberModel.user_id == user_id,
                TeamMemberModel.is_active == True
            )
        )
        return result.scalar_one_or_none()


class FAQRepository(BaseRepository[FAQModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, FAQModel)

    async def get_by_business(self, business_id: str) -> List[FAQModel]:
        result = await self.session.execute(
            select(FAQModel)
            .where(FAQModel.business_id == business_id, FAQModel.is_active == True)
        )
        return list(result.scalars().all())

    async def search(self, business_id: str, query: str) -> List[FAQModel]:
        result = await self.session.execute(
            select(FAQModel)
            .where(
                FAQModel.business_id == business_id,
                FAQModel.is_active == True,
                FAQModel.question.ilike(f"%{query}%")
            )
        )
        return list(result.scalars().all())
