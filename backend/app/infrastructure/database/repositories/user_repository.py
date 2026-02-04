from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .base_repository import BaseRepository
from ..models import UserModel, AddressModel


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.email == email, UserModel.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[UserModel]:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.phone == phone, UserModel.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_auth(self, auth_provider: str, auth_id: str) -> Optional[UserModel]:
        result = await self.session.execute(
            select(UserModel)
            .where(
                UserModel.auth_provider == auth_provider,
                UserModel.auth_id == auth_id,
                UserModel.is_active == True
            )
        )
        return result.scalar_one_or_none()


class AddressRepository(BaseRepository[AddressModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AddressModel)

    async def get_by_user(self, user_id: str) -> List[AddressModel]:
        result = await self.session.execute(
            select(AddressModel)
            .where(AddressModel.user_id == user_id, AddressModel.is_active == True)
        )
        return list(result.scalars().all())
