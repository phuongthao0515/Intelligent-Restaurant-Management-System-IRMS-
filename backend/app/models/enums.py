from enum import Enum


class StaffRole(str, Enum):
    MANAGER = "MANAGER"
    SERVER = "SERVER"
    CHEF = "CHEF"
    CASHIER = "CASHIER"
    HOST = "HOST"


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    IN_KITCHEN = "IN_KITCHEN"
    READY = "READY"
    SERVED = "SERVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class OrderPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    VIP = "VIP"


class OrderItemStatus(str, Enum):
    QUEUED = "QUEUED"
    PREPARING = "PREPARING"
    READY = "READY"
    SERVED = "SERVED"
    VOIDED = "VOIDED"


class TableStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    CLEANING = "CLEANING"


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SEATED = "SEATED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    WALLET = "WALLET"


class OrderEventType(str, Enum):
    PLACED = "PLACED"
    STATUS_CHANGED = "STATUS_CHANGED"
    ITEM_STATUS_CHANGED = "ITEM_STATUS_CHANGED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    RECALLED = "RECALLED"
