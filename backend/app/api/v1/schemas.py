from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from app.domain.shared.enums import (
    CartStatus, CartItemStatus, BillStatus, PaymentMethod, 
    AssistantType, OrderSource, IntentType
)


class CategoryCreate(BaseModel):
    business_id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class MenuItemCreate(BaseModel):
    business_id: str
    category_id: str
    name: str
    price: Decimal
    description: Optional[str] = None
    image_url: Optional[str] = None
    preparation_time_mins: int = 10
    quantity: int = 100


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None
    preparation_time_mins: Optional[int] = None
    quantity: Optional[int] = None


class CartCreate(BaseModel):
    business_id: str
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    source: OrderSource = OrderSource.APP
    intent: IntentType = IntentType.FOOD_ORDER


class CartItemAdd(BaseModel):
    item_id: str
    quantity: int = 1
    notes: Optional[str] = None


class CartItemUpdate(BaseModel):
    cart_item_id: str
    quantity: int


class CartConfirm(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    resource_id: Optional[str] = None
    estimated_ready_time: Optional[int] = None


class CartStatusUpdate(BaseModel):
    status: CartStatus


class CartItemStatusUpdate(BaseModel):
    status: CartItemStatus
    prepared_by: Optional[str] = None


class BillCreate(BaseModel):
    cart_id: str
    tax_percent: Decimal = Decimal("5.0")
    discount_amount: Decimal = Decimal("0")
    service_charge: Decimal = Decimal("0")


class PaymentProcess(BaseModel):
    amount: Decimal
    payment_mode: PaymentMethod
    payment_ref: Optional[str] = None


class SplitPayment(BaseModel):
    bill_item_ids: List[str]
    paid_by_user_id: str
    amount: Decimal
    payment_mode: PaymentMethod


class AssistantSessionCreate(BaseModel):
    assistant_type: AssistantType
    device_id: Optional[str] = None
    phone_number: Optional[str] = None


class AssistantTextInput(BaseModel):
    session_id: str
    text: str
    device_id: str
    business_id: str = "1"


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
