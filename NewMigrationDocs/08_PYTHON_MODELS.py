"""
SQLAlchemy Models for Multi-Tenant Schema
All tables use UUID (String 36) as primary keys
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Numeric, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base
from app.domain.shared.enums import (
    BusinessType, PaymentFlow, ResourceType, ResourceStatus,
    CartStatus, CartItemStatus, BillStatus, BillItemStatus,
    PaymentMethod, UserRole, OrderSource, IntentType,
    AssistantType, ConversationStatus, DeviceType, AddressType, TeamMemberStatus
)


def generate_uuid():
    return str(uuid.uuid4())


class BusinessModel(Base):
    __tablename__ = "businesses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    type = Column(SQLEnum(BusinessType), nullable=False)
    intents = Column(String(100))
    requires_approval = Column(Boolean, default=True)
    payment_flow = Column(SQLEnum(PaymentFlow), default=PaymentFlow.POST_SERVICE)
    payment_modes = Column(String(100))
    resource_type = Column(SQLEnum(ResourceType))
    contact_phone = Column(String(20))
    timings = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    resources = relationship("ResourceModel", back_populates="business")
    categories = relationship("CategoryModel", back_populates="business")
    menu_items = relationship("MenuModel", back_populates="business")
    team_members = relationship("TeamMemberModel", back_populates="business")
    carts = relationship("CartModel", back_populates="business")
    bills = relationship("BillModel", back_populates="business")
    faqs = relationship("FAQModel", back_populates="business")


class ResourceModel(Base):
    __tablename__ = "resources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    type = Column(SQLEnum(ResourceType), nullable=False)
    name = Column(String(200), nullable=False)
    capacity = Column(Integer, default=1)
    meta_json = Column(JSON, default=dict)
    status = Column(SQLEnum(ResourceStatus), default=ResourceStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    business = relationship("BusinessModel", back_populates="resources")
    carts = relationship("CartModel", back_populates="resource")


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    business = relationship("BusinessModel", back_populates="categories")
    menu_items = relationship("MenuModel", back_populates="category")


class MenuModel(Base):
    __tablename__ = "menu"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String(500))
    available = Column(Boolean, default=True)
    quantity = Column(Integer, default=100)
    preparation_time_mins = Column(Integer, default=10)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    business = relationship("BusinessModel", back_populates="menu_items")
    category = relationship("CategoryModel", back_populates="menu_items")
    cart_items = relationship("CartItemModel", back_populates="menu_item")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(255))
    hashed_password = Column(String(255))
    auth_provider = Column(String(50))
    auth_id = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    team_memberships = relationship("TeamMemberModel", back_populates="user")
    carts = relationship("CartModel", back_populates="user")
    addresses = relationship("AddressModel", back_populates="user")
    paid_bill_items = relationship("BillItemModel", back_populates="paid_by_user")


class TeamMemberModel(Base):
    __tablename__ = "team_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STAFF)
    status = Column(SQLEnum(TeamMemberStatus), default=TeamMemberStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    business = relationship("BusinessModel", back_populates="team_members")
    user = relationship("UserModel", back_populates="team_memberships")
    prepared_items = relationship("CartItemModel", back_populates="prepared_by_member")


class AddressModel(Base):
    __tablename__ = "addresses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(AddressType), nullable=False)
    address_line1 = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    pincode = Column(String(20), nullable=False)
    lat_long = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    user = relationship("UserModel", back_populates="addresses")


class CartModel(Base):
    __tablename__ = "carts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(100))
    device_id = Column(String(100))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    intent = Column(SQLEnum(IntentType), default=IntentType.FOOD_ORDER)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=True)
    customer_name = Column(String(200))
    customer_phone = Column(String(20))
    item_count = Column(Integer, default=0)
    subtotal = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), default=0)
    status = Column(SQLEnum(CartStatus), default=CartStatus.DRAFT)
    source = Column(SQLEnum(OrderSource), default=OrderSource.APP)
    notes = Column(Text)
    estimated_ready_time = Column(Integer)
    assistant_session_id = Column(String(36), ForeignKey("assistant_sessions.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    user = relationship("UserModel", back_populates="carts")
    business = relationship("BusinessModel", back_populates="carts")
    resource = relationship("ResourceModel", back_populates="carts")
    items = relationship("CartItemModel", back_populates="cart")
    bill = relationship("BillModel", back_populates="cart", uselist=False)
    assistant_session = relationship("AssistantSessionModel", back_populates="carts")


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id"), nullable=False)
    item_id = Column(String(36), ForeignKey("menu.id"), nullable=False)
    item_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text)
    status = Column(SQLEnum(CartItemStatus), default=CartItemStatus.DRAFT)
    prepared_by = Column(String(36), ForeignKey("team_members.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    cart = relationship("CartModel", back_populates="items")
    menu_item = relationship("MenuModel", back_populates="cart_items")
    prepared_by_member = relationship("TeamMemberModel", back_populates="prepared_items")
    bill_items = relationship("BillItemModel", back_populates="cart_item")


class BillModel(Base):
    __tablename__ = "bills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id"), nullable=False)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    subtotal = Column(Numeric(10, 2), default=0)
    tax_percent = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    service_charge = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)
    paid_amount = Column(Numeric(10, 2), default=0)
    payment_mode = Column(SQLEnum(PaymentMethod), nullable=True)
    status = Column(SQLEnum(BillStatus), default=BillStatus.PENDING)
    payment_ref = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    cart = relationship("CartModel", back_populates="bill")
    business = relationship("BusinessModel", back_populates="bills")
    items = relationship("BillItemModel", back_populates="bill")


class BillItemModel(Base):
    __tablename__ = "bill_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bill_id = Column(String(36), ForeignKey("bills.id"), nullable=False)
    cart_item_id = Column(String(36), ForeignKey("cart_items.id"), nullable=False)
    item_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    paid_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(BillItemStatus), default=BillItemStatus.UNPAID)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    bill = relationship("BillModel", back_populates="items")
    cart_item = relationship("CartItemModel", back_populates="bill_items")
    paid_by_user = relationship("UserModel", back_populates="paid_bill_items")


class FAQModel(Base):
    __tablename__ = "faqs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    business = relationship("BusinessModel", back_populates="faqs")


class AssistantSessionModel(Base):
    __tablename__ = "assistant_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(100), unique=True, nullable=False)
    assistant_type = Column(SQLEnum(AssistantType), nullable=False)
    device_id = Column(String(100))
    phone_number = Column(String(20))
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    context = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    messages = relationship("ConversationMessageModel", back_populates="session")
    carts = relationship("CartModel", back_populates="assistant_session")


class ConversationMessageModel(Base):
    __tablename__ = "conversation_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("assistant_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    audio_url = Column(String(500))
    intent = Column(String(100))
    entities = Column(JSON, default=dict)
    confidence = Column(Numeric(5, 4))
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AssistantSessionModel", back_populates="messages")


class DeviceModel(Base):
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200))
    device_type = Column(SQLEnum(DeviceType))
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
