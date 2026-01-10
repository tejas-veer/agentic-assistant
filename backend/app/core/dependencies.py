from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import async_session_factory
from app.services.menu_service import MenuService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.assistant_service import AssistantService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class ServiceFactory:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._menu_service = None
        self._cart_service = None
        self._order_service = None
        self._assistant_service = None
    
    @property
    def menu(self) -> MenuService:
        if self._menu_service is None:
            self._menu_service = MenuService(self.session)
        return self._menu_service
    
    @property
    def cart(self) -> CartService:
        if self._cart_service is None:
            self._cart_service = CartService(self.session)
        return self._cart_service
    
    @property
    def order(self) -> OrderService:
        if self._order_service is None:
            self._order_service = OrderService(self.session)
        return self._order_service
    
    @property
    def assistant(self) -> AssistantService:
        if self._assistant_service is None:
            self._assistant_service = AssistantService(self.session)
        return self._assistant_service


async def get_services(session: AsyncSession) -> ServiceFactory:
    return ServiceFactory(session)

