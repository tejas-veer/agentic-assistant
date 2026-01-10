from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    WALLET = "wallet"


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    STAFF = "staff"


class DeviceType(str, Enum):
    KIOSK = "kiosk"
    TABLET = "tablet"
    WEB = "web"
    PHONE = "phone"


class AssistantType(str, Enum):
    VOICE = "voice"
    CALL = "call"
    CHAT = "chat"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

