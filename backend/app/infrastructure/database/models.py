from sqlalchemy import Column, String, DateTime, Boolean, Integer, Numeric, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .connection import Base
from app.domain.shared.enums import OrderStatus, PaymentStatus, PaymentMethod, AssistantType, ConversationStatus


def generate_uuid():
    return str(uuid.uuid4())


class CategoryModel(Base):
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    menu_items = relationship("MenuItemModel", back_populates="category")


class MenuItemModel(Base):
    __tablename__ = "menu_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"))
    image_url = Column(String(500))
    is_available = Column(Boolean, default=True)
    preparation_time_mins = Column(Integer, default=10)
    tags = Column(JSON, default=list)
    customizations = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    category = relationship("CategoryModel", back_populates="menu_items")


class OrderModel(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_number = Column(String(20), unique=True, nullable=False)
    device_id = Column(String(100))
    table_number = Column(String(20))
    customer_name = Column(String(200))
    customer_phone = Column(String(20))
    items = Column(JSON, nullable=False)
    subtotal = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), default=0)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(SQLEnum(PaymentMethod))
    notes = Column(Text)
    estimated_ready_time = Column(Integer)
    assistant_session_id = Column(String(36))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class CartModel(Base):
    __tablename__ = "carts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(100), unique=True, nullable=False)
    device_id = Column(String(100))
    items = Column(JSON, default=list)
    subtotal = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class AssistantSessionModel(Base):
    __tablename__ = "assistant_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(100), unique=True, nullable=False)
    assistant_type = Column(SQLEnum(AssistantType), nullable=False)
    device_id = Column(String(100))
    phone_number = Column(String(20))
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    context = Column(JSON, default=dict)
    order_id = Column(String(36))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class ConversationMessageModel(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("assistant_sessions.id"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    audio_url = Column(String(500))
    intent = Column(String(100))
    entities = Column(JSON, default=dict)
    confidence = Column(Numeric(5, 4))
    created_at = Column(DateTime, default=datetime.utcnow)


class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(20), default="staff")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class DeviceModel(Base):
    __tablename__ = "devices"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200))
    device_type = Column(String(20))
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

