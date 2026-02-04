"""
Python Enums for the new schema
Copy this to: backend/app/domain/shared/enums.py
"""

from enum import Enum


class BusinessType(str, Enum):
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    CLINIC = "clinic"


class PaymentFlow(str, Enum):
    PRE_SERVICE = "pre_service"
    POST_SERVICE = "post_service"


class ResourceType(str, Enum):
    TABLE = "table"
    ROOM = "room"
    SLOT = "slot"


class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"


class CartStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    CANCELLED = "cancelled"


class CartItemStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    ABANDONED = "abandoned"
    CANCELLED = "cancelled"


class BillStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"


class BillItemStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CASH = "cash"
    UPI = "upi"
    CARD = "card"


class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"


class OrderSource(str, Enum):
    APP = "app"
    VOICE = "voice"
    CHAT = "chat"


class IntentType(str, Enum):
    FOOD_ORDER = "food_order"
    BOOKING = "booking"
    APPOINTMENT = "appointment"


class AssistantType(str, Enum):
    VOICE = "voice"
    CALL = "call"
    CHAT = "chat"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
