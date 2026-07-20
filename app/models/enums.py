from enum import Enum

class UserRole(str, Enum):
    client = "client"
    waiter = "waiter"
    admin = "admin"

class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"

class ReservationStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
