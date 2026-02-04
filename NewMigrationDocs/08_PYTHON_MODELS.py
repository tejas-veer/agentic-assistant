"""
SQLAlchemy Models for the new schema
Copy this to: backend/app/infrastructure/database/models.py
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Numeric, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Import your Base from connection.py
# from .connection import Base

# Import enums
# from app.domain.shared.enums import (
#     BusinessType, PaymentFlow, ResourceType, ResourceStatus,
#     CartStatus, CartItemStatus, BillStatus, BillItemStatus,
#     PaymentMethod, UserRole, OrderSource, IntentType
# )


def generate_uuid():
    return str(uuid.uuid4())


class BusinessModel:
    """
    __tablename__ = "businesses"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)  # SQLEnum(BusinessType)
    intents = Column(String(100))
    requires_approval = Column(Boolean, default=True)
    payment_flow = Column(String(20), default='post_service')
    payment_modes = Column(String(100))
    resource_type = Column(String(20))
    contact_phone = Column(String(20))
    timings = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # resources = relationship("ResourceModel", back_populates="business")
    # menu_items = relationship("MenuModel", back_populates="business")
    # team_members = relationship("TeamMemberModel", back_populates="business")
    # carts = relationship("CartModel", back_populates="business")


class ResourceModel:
    """
    __tablename__ = "resources"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(20), unique=True, nullable=False)
    business_id = Column(String(36), ForeignKey("businesses.id"))
    type = Column(String(20), nullable=False)  # TABLE, ROOM, SLOT
    name = Column(String(200), nullable=False)
    capacity = Column(Integer, default=1)
    meta_json = Column(JSON, default=dict)
    status = Column(String(20), default='available')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # business = relationship("BusinessModel", back_populates="resources")
    # carts = relationship("CartModel", back_populates="resource")


class MenuModel:
    """
    __tablename__ = "menu"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_id = Column(String(20), unique=True, nullable=False)
    business_id = Column(String(36), ForeignKey("businesses.id"))
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    price = Column(Numeric(10, 2), nullable=False)
    available = Column(Boolean, default=True)
    quantity = Column(Integer, default=100)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # business = relationship("BusinessModel", back_populates="menu_items")
    # cart_items = relationship("CartItemModel", back_populates="menu_item")


class UserModel:
    """
    __tablename__ = "users"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(255))
    auth_provider = Column(String(50))
    auth_id = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # team_memberships = relationship("TeamMemberModel", back_populates="user")
    # carts = relationship("CartModel", back_populates="user")
    # addresses = relationship("AddressModel", back_populates="user")


class TeamMemberModel:
    """
    __tablename__ = "team_members"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    member_id = Column(String(20), unique=True, nullable=False)
    business_id = Column(String(36), ForeignKey("businesses.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    role = Column(String(20), default='staff')  # ADMIN, STAFF
    status = Column(String(20), default='active')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # business = relationship("BusinessModel", back_populates="team_members")
    # user = relationship("UserModel", back_populates="team_memberships")
    # prepared_items = relationship("CartItemModel", back_populates="prepared_by_member")


class AddressModel:
    """
    __tablename__ = "addresses"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    address_id = Column(String(20), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"))
    type = Column(String(20))  # HOME, WORK, OTHER
    address_line1 = Column(String(500))
    city = Column(String(100))
    pincode = Column(String(20))
    lat_long = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # user = relationship("UserModel", back_populates="addresses")


class CartModel:
    """
    __tablename__ = "carts"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(20), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    business_id = Column(String(36), ForeignKey("businesses.id"))
    intent = Column(String(20), default='food_order')
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=True)
    customer_name = Column(String(200))
    customer_phone = Column(String(20))
    item_count = Column(Integer, default=0)
    subtotal = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default='draft')
    source = Column(String(20), default='app')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # user = relationship("UserModel", back_populates="carts")
    # business = relationship("BusinessModel", back_populates="carts")
    # resource = relationship("ResourceModel", back_populates="carts")
    # items = relationship("CartItemModel", back_populates="cart")
    # bill = relationship("BillModel", back_populates="cart", uselist=False)


class CartItemModel:
    """
    __tablename__ = "cart_items"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_item_id = Column(String(20), unique=True, nullable=False)
    cart_id = Column(String(36), ForeignKey("carts.id"))
    item_id = Column(String(36), ForeignKey("menu.id"))
    item_name = Column(String(200))
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2))
    total_price = Column(Numeric(10, 2))
    notes = Column(Text)
    status = Column(String(20), default='draft')
    prepared_by = Column(String(36), ForeignKey("team_members.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # cart = relationship("CartModel", back_populates="items")
    # menu_item = relationship("MenuModel", back_populates="cart_items")
    # prepared_by_member = relationship("TeamMemberModel", back_populates="prepared_items")
    # bill_items = relationship("BillItemModel", back_populates="cart_item")


class BillModel:
    """
    __tablename__ = "bills"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bill_id = Column(String(20), unique=True, nullable=False)
    cart_id = Column(String(36), ForeignKey("carts.id"))
    business_id = Column(String(36), ForeignKey("businesses.id"))
    subtotal = Column(Numeric(10, 2), default=0)
    tax_percent = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    service_charge = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)
    paid_amount = Column(Numeric(10, 2), default=0)
    payment_mode = Column(String(20), nullable=True)
    status = Column(String(20), default='pending')
    payment_ref = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # cart = relationship("CartModel", back_populates="bill")
    # items = relationship("BillItemModel", back_populates="bill")


class BillItemModel:
    """
    __tablename__ = "bill_items"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bill_item_id = Column(String(20), unique=True, nullable=False)
    bill_id = Column(String(36), ForeignKey("bills.id"))
    cart_item_id = Column(String(36), ForeignKey("cart_items.id"))
    item_name = Column(String(200))
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2))
    total_price = Column(Numeric(10, 2))
    paid_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default='unpaid')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    # bill = relationship("BillModel", back_populates="items")
    # cart_item = relationship("CartItemModel", back_populates="bill_items")


class FAQModel:
    """
    __tablename__ = "faqs"
    """
    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
