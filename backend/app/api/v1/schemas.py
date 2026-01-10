from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from app.domain.shared.enums import OrderStatus, PaymentStatus, PaymentMethod, AssistantType


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class MenuItemCreate(BaseModel):
    name: str
    price: Decimal
    category_id: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    preparation_time_mins: int = 10
    tags: List[str] = Field(default_factory=list)
    customizations: List[Dict[str, Any]] = Field(default_factory=list)


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    preparation_time_mins: Optional[int] = None
    tags: Optional[List[str]] = None
    customizations: Optional[List[Dict[str, Any]]] = None


class CartItemAdd(BaseModel):
    menu_item_id: str
    quantity: int = 1
    customizations: List[str] = Field(default_factory=list)
    special_instructions: Optional[str] = None


class CartItemUpdate(BaseModel):
    menu_item_id: str
    quantity: int


class OrderCreate(BaseModel):
    session_id: str
    table_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderConfirm(BaseModel):
    estimated_ready_time: Optional[int] = None


class PaymentUpdate(BaseModel):
    payment_status: PaymentStatus
    payment_method: Optional[PaymentMethod] = None


class AssistantSessionCreate(BaseModel):
    assistant_type: AssistantType
    device_id: Optional[str] = None
    phone_number: Optional[str] = None


class AssistantTextInput(BaseModel):
    session_id: str
    text: str
    device_id: str


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

