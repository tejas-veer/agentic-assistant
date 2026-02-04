from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.business_repository import TeamMemberRepository
from app.infrastructure.database.models import UserModel, TeamMemberModel
from app.domain.shared.enums import UserRole, TeamMemberStatus
from app.core.config import settings
from app.utils.null_check import Util

SECRET_KEY = settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt, stored_hash = hashed_password.split(':')
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == stored_hash
    except:
        return False


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.team_member_repo = TeamMemberRepository(session)
        self.session = session

    async def signup(
        self,
        name: str,
        email: str,
        password: str,
        phone: str = None
    ) -> dict:
        existing = await self.user_repo.get_by_email(email)
        if Util.is_not_null(existing):
            raise ValueError("Email already registered")

        hashed_password = hash_password(password)
        user = UserModel(
            name=name,
            email=email,
            phone=phone,
            hashed_password=hashed_password,
            auth_provider="email"
        )
        user = await self.user_repo.create(user)

        token = create_access_token({"sub": user.id, "email": user.email})
        
        return {
            "user": self._user_to_dict(user),
            "token": token
        }

    async def signin(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if Util.is_null(user):
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.hashed_password or ""):
            raise ValueError("Invalid email or password")

        token = create_access_token({"sub": user.id, "email": user.email})

        team_memberships = await self.team_member_repo.get_by_user(user.id)
        
        return {
            "user": self._user_to_dict(user),
            "token": token,
            "memberships": [self._membership_to_dict(m) for m in team_memberships]
        }

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        user = await self.user_repo.get_by_id(user_id)
        if Util.is_null(user):
            return None
        return self._user_to_dict(user)

    async def get_user_memberships(self, user_id: str) -> list:
        memberships = await self.team_member_repo.get_by_user(user_id)
        return [self._membership_to_dict(m) for m in memberships]

    async def assign_role(
        self,
        assigner_user_id: str,
        business_id: str,
        target_user_id: str,
        role: UserRole
    ) -> dict:
        assigner_membership = await self.team_member_repo.get_by_business_and_user(business_id, assigner_user_id)
        if Util.is_null(assigner_membership) or assigner_membership.role != UserRole.ADMIN:
            raise ValueError("Only admins can assign roles")

        existing = await self.team_member_repo.get_by_business_and_user(business_id, target_user_id)
        if Util.is_not_null(existing):
            await self.team_member_repo.update(existing.id, {"role": role})
            existing = await self.team_member_repo.get_by_id(existing.id)
            return self._membership_to_dict(existing)

        membership = TeamMemberModel(
            business_id=business_id,
            user_id=target_user_id,
            role=role,
            status=TeamMemberStatus.ACTIVE
        )
        membership = await self.team_member_repo.create(membership)
        return self._membership_to_dict(membership)

    async def remove_role(
        self,
        assigner_user_id: str,
        business_id: str,
        target_user_id: str
    ) -> bool:
        assigner_membership = await self.team_member_repo.get_by_business_and_user(business_id, assigner_user_id)
        if Util.is_null(assigner_membership) or assigner_membership.role != UserRole.ADMIN:
            raise ValueError("Only admins can remove roles")

        existing = await self.team_member_repo.get_by_business_and_user(business_id, target_user_id)
        if Util.is_not_null(existing):
            await self.team_member_repo.update(existing.id, {"is_active": False})
            return True
        return False

    async def get_business_members(self, business_id: str) -> list:
        memberships = await self.team_member_repo.get_by_business(business_id)
        result = []
        for m in memberships:
            data = self._membership_to_dict(m)
            user = await self.user_repo.get_by_id(m.user_id)
            if user:
                data["user"] = self._user_to_dict(user)
            result.append(data)
        return result

    def _user_to_dict(self, user: UserModel) -> dict:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "isActive": user.is_active,
            "createdAt": user.created_at.isoformat() if user.created_at else None
        }

    def _membership_to_dict(self, membership: TeamMemberModel) -> dict:
        return {
            "id": membership.id,
            "businessId": membership.business_id,
            "userId": membership.user_id,
            "role": membership.role.value if membership.role else None,
            "status": membership.status.value if membership.status else None,
            "isActive": membership.is_active,
            "createdAt": membership.created_at.isoformat() if membership.created_at else None
        }
