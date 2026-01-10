from typing import Optional, List
from pydantic import Field
from decimal import Decimal
from ..shared.base_entity import AuditableEntity
from ..shared.enums import OrderStatus, PaymentStatus, PaymentMethod


class Category(AuditableEntity):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int = 0


class MenuItem(AuditableEntity):
    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: str
    image_url: Optional[str] = None
    is_available: bool = True
    preparation_time_mins: int = 10
    tags: List[str] = Field(default_factory=list)
    customizations: List["MenuItemCustomization"] = Field(default_factory=list)


class MenuItemCustomization(AuditableEntity):
    name: str
    options: List["CustomizationOption"] = Field(default_factory=list)
    is_required: bool = False
    max_selections: int = 1


class CustomizationOption(AuditableEntity):
    name: str
    price_modifier: Decimal = Decimal("0.00")


class OrderItem(AuditableEntity):
    menu_item_id: str
    menu_item_name: str
    quantity: int = 1
    unit_price: Decimal
    total_price: Decimal
    customizations: List[str] = Field(default_factory=list)
    special_instructions: Optional[str] = None


class Order(AuditableEntity):
    order_number: str
    device_id: str
    table_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    items: List[OrderItem] = Field(default_factory=list)
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    discount: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None
    estimated_ready_time: Optional[int] = None
    assistant_session_id: Optional[str] = None


class Cart(AuditableEntity):
    session_id: str
    device_id: str
    items: List[OrderItem] = Field(default_factory=list)
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")

