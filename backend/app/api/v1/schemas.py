from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.domain.shared.enums import (
    CartStatus, CartItemStatus, BillStatus, BillItemStatus, PaymentMethod, 
    AssistantType, OrderSource, IntentType, ResourceStatus, ResourceType,
    BusinessType, PaymentFlow, UserRole, TeamMemberStatus, AddressType,
    ConversationStatus, DeviceType
)


def to_camel(string: str) -> str:
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )


class BusinessResponse(CamelModel):
    id: str
    name: str
    type: BusinessType
    intents: Optional[str] = None
    requires_approval: bool
    payment_flow: PaymentFlow
    payment_modes: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    contact_phone: Optional[str] = None
    timings: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ResourceResponse(CamelModel):
    id: str
    business_id: str
    type: ResourceType
    name: str
    capacity: int
    meta_json: Optional[Dict[str, Any]] = None
    status: ResourceStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class CategoryResponse(CamelModel):
    id: str
    business_id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: Optional[List["MenuItemResponse"]] = None


class MenuItemResponse(CamelModel):
    id: str
    business_id: str
    category_id: str
    name: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    available: bool
    quantity: int
    preparation_time_mins: int
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserResponse(CamelModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    auth_provider: Optional[str] = None
    auth_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class TeamMemberResponse(CamelModel):
    id: str
    business_id: str
    user_id: str
    role: UserRole
    status: TeamMemberStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None


class AddressResponse(CamelModel):
    id: str
    user_id: str
    type: AddressType
    address_line1: str
    city: str
    pincode: str
    lat_long: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class CartItemResponse(CamelModel):
    id: str
    cart_id: str
    item_id: str
    item_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    notes: Optional[str] = None
    status: CartItemStatus
    prepared_by: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    menu_item: Optional[MenuItemResponse] = None


class CartResponse(CamelModel):
    id: str
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    user_id: Optional[str] = None
    business_id: str
    intent: IntentType
    resource_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    item_count: int
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    status: CartStatus
    source: OrderSource
    notes: Optional[str] = None
    estimated_ready_time: Optional[int] = None
    assistant_session_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: Optional[List[CartItemResponse]] = None
    resource: Optional[ResourceResponse] = None


class BillItemResponse(CamelModel):
    id: str
    bill_id: str
    cart_item_id: str
    item_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    paid_by_user_id: Optional[str] = None
    status: BillItemStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class BillResponse(CamelModel):
    id: str
    cart_id: str
    business_id: str
    subtotal: Decimal
    tax_percent: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    service_charge: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    payment_mode: Optional[PaymentMethod] = None
    status: BillStatus
    payment_ref: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: Optional[List[BillItemResponse]] = None


class FAQResponse(CamelModel):
    id: str
    business_id: str
    question: str
    answer: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ConversationMessageResponse(CamelModel):
    id: str
    session_id: str
    role: str
    content: str
    audio_url: Optional[str] = None
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    confidence: Optional[Decimal] = None
    created_at: datetime


class AssistantSessionResponse(CamelModel):
    id: str
    session_id: str
    assistant_type: AssistantType
    device_id: Optional[str] = None
    phone_number: Optional[str] = None
    status: ConversationStatus
    context: Optional[Dict[str, Any]] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: Optional[List[ConversationMessageResponse]] = None


class DeviceResponse(CamelModel):
    id: str
    device_id: str
    name: Optional[str] = None
    device_type: Optional[DeviceType] = None
    location: Optional[str] = None
    is_active: bool
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


CategoryResponse.model_rebuild()


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
    user_id: Optional[str] = None
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
    business_id: str = "biz00001-0000-0000-0000-000000000001"


class ApiResponse(CamelModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
