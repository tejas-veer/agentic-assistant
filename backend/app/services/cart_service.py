from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.infrastructure.database.repositories.order_repository import CartRepository
from app.infrastructure.database.repositories.menu_repository import MenuItemRepository
from app.infrastructure.database.models import CartModel
from app.utils.null_check import Util


TAX_RATE = Decimal("0.10")


class CartService:
    def __init__(self, session: AsyncSession):
        self.cart_repo = CartRepository(session)
        self.menu_repo = MenuItemRepository(session)
        self.session = session
    
    async def get_or_create_cart(self, session_id: str, device_id: str) -> CartModel:
        cart = await self.cart_repo.get_by_session(session_id)
        if Util.is_null(cart):
            cart = CartModel(
                session_id=session_id,
                device_id=device_id,
                items=[],
                subtotal=Decimal("0.00"),
                tax=Decimal("0.00"),
                total=Decimal("0.00")
            )
            cart = await self.cart_repo.create(cart)
        return cart
    
    async def add_item(
        self,
        session_id: str,
        device_id: str,
        menu_item_id: str,
        quantity: int = 1,
        customizations: List[str] = None,
        special_instructions: str = None
    ) -> Dict[str, Any]:
        cart = await self.get_or_create_cart(session_id, device_id)
        menu_item = await self.menu_repo.get_by_id(menu_item_id)
        
        if Util.is_null(menu_item):
            raise ValueError("Menu item not found")
        
        if not menu_item.is_available:
            raise ValueError("Menu item is not available")
        
        items = list(cart.items) if cart.items else []
        
        existing_item_idx = None
        for idx, item in enumerate(items):
            if (item.get("menu_item_id") == menu_item_id and 
                item.get("customizations") == (customizations or []) and
                item.get("special_instructions") == special_instructions):
                existing_item_idx = idx
                break
        
        unit_price = float(menu_item.price)
        
        if existing_item_idx is not None:
            items[existing_item_idx]["quantity"] += quantity
            items[existing_item_idx]["total_price"] = items[existing_item_idx]["quantity"] * unit_price
        else:
            items.append({
                "menu_item_id": menu_item_id,
                "menu_item_name": menu_item.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": quantity * unit_price,
                "customizations": customizations or [],
                "special_instructions": special_instructions
            })
        
        return await self._update_cart_totals(cart, items)
    
    async def update_item_quantity(
        self,
        session_id: str,
        menu_item_id: str,
        quantity: int
    ) -> Dict[str, Any]:
        cart = await self.cart_repo.get_by_session(session_id)
        if Util.is_null(cart):
            raise ValueError("Cart not found")
        
        items = list(cart.items) if cart.items else []
        
        if quantity <= 0:
            items = [item for item in items if item.get("menu_item_id") != menu_item_id]
        else:
            for item in items:
                if item.get("menu_item_id") == menu_item_id:
                    item["quantity"] = quantity
                    item["total_price"] = quantity * item["unit_price"]
                    break
        
        return await self._update_cart_totals(cart, items)
    
    async def remove_item(self, session_id: str, menu_item_id: str) -> Dict[str, Any]:
        return await self.update_item_quantity(session_id, menu_item_id, 0)
    
    async def clear_cart(self, session_id: str) -> bool:
        return await self.cart_repo.clear_cart(session_id)
    
    async def get_cart(self, session_id: str) -> Optional[Dict[str, Any]]:
        cart = await self.cart_repo.get_by_session(session_id)
        if Util.is_null(cart):
            return None
        
        return {
            "id": cart.id,
            "session_id": cart.session_id,
            "device_id": cart.device_id,
            "items": cart.items or [],
            "subtotal": float(cart.subtotal),
            "tax": float(cart.tax),
            "total": float(cart.total)
        }
    
    async def _update_cart_totals(self, cart: CartModel, items: List[Dict]) -> Dict[str, Any]:
        subtotal = Decimal(sum(item.get("total_price", 0) for item in items))
        tax = subtotal * TAX_RATE
        total = subtotal + tax
        
        await self.cart_repo.update(cart.id, {
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "total": total
        })
        
        return {
            "id": cart.id,
            "session_id": cart.session_id,
            "device_id": cart.device_id,
            "items": items,
            "subtotal": float(subtotal),
            "tax": float(tax),
            "total": float(total)
        }

