"""
Modelos de MongoDB usando Beanie ODM
"""
from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    """Roles de usuario"""
    CLIENT = "cliente"
    ADMIN = "administrativo"


class User(Document):
    """Modelo de usuario en MongoDB"""
    full_name: str = Field(..., max_length=120)
    email: Indexed(EmailStr, unique=True)
    phone: Optional[str] = Field(None, max_length=30)
    password_hash: Optional[str] = Field(None, max_length=255)
    google_id: Optional[Indexed(str, unique=True)] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    role: UserRole = Field(default=UserRole.CLIENT)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "google_id",
            "role"
        ]


class PasswordResetToken(Document):
    """Tokens de reseteo de contraseña"""
    user_id: str  # ObjectId como string
    token_hash: Indexed(str, unique=True) = Field(..., max_length=64)
    expires_at: datetime
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "password_reset_tokens"
        indexes = [
            "user_id",
            "token_hash",
            "expires_at"
        ]


class VehicleType(str, Enum):
    """Tipos de vehículos disponibles"""
    VAN = "van"
    PICKUP = "pickup"
    TRUCK = "truck"
    SUV = "suv"
    MINIBUS = "minibus"


class VehicleStatus(str, Enum):
    """Estados del vehículo"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class Vehicle(Document):
    """Modelo de vehículos/transportes disponibles"""
    brand: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    year: int
    vehicle_type: str = Field(..., max_length=50)
    capacity: int
    plate: Indexed(str, unique=True) = Field(..., max_length=20)
    color: Optional[str] = Field(None, max_length=50)
    
    # Precios
    price_per_day: float
    price_per_hour: Optional[float] = None
    
    # Detalles
    description: Optional[str] = None
    features: Optional[str] = None  # JSON string
    image_url: Optional[str] = Field(None, max_length=500)
    
    # Estado
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE)
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "vehicles"
        indexes = [
            "plate",
            "vehicle_type",
            "status",
            "is_active"
        ]


class ReservationStatus(str, Enum):
    """Estados de la reservación"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Reservation(Document):
    """Modelo de reservaciones"""
    user_id: str  # ObjectId como string
    vehicle_id: str  # ObjectId como string
    
    # Fechas
    start_date: datetime
    end_date: datetime
    
    # Detalles de la reservación
    pickup_location: str = Field(..., max_length=200)
    return_location: Optional[str] = Field(None, max_length=200)
    
    # Precios
    total_days: int
    price_per_day: float
    total_price: float
    
    # Estado y notas
    status: ReservationStatus = Field(default=ReservationStatus.PENDING)
    notes: Optional[str] = None
    admin_notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    class Settings:
        name = "reservations"
        indexes = [
            "user_id",
            "vehicle_id",
            "status",
            "start_date",
            "end_date"
        ]


class Review(Document):
    """Modelo de reviews/calificaciones"""
    usuario: str = Field(..., min_length=2, max_length=100)
    calificacion: int = Field(..., ge=1, le=5)
    comentario: str = Field(..., min_length=10, max_length=500)
    fecha: datetime = Field(default_factory=datetime.utcnow)
    vehicle_id: Optional[str] = None  # Opcional: relacionar con vehículo
    user_id: Optional[str] = None  # Opcional: relacionar con usuario
    
    class Settings:
        name = "reviews"
        indexes = [
            "fecha",
            "calificacion"
        ]


class NewsletterSubscriber(Document):
    """Suscriptores del newsletter"""
    email: Indexed(EmailStr, unique=True)
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = Field(default=True)
    
    class Settings:
        name = "newsletter_subscribers"
        indexes = [
            "email",
            "active"
        ]


class Promotion(Document):
    """Promociones activas"""
    titulo: str = Field(..., max_length=200)
    descripcion: str
    descuento: float = Field(..., ge=0, le=100)
    imagen_url: Optional[str] = Field(None, max_length=500)
    fecha_inicio: datetime
    fecha_fin: datetime
    activa: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "promotions"
        indexes = [
            "activa",
            "fecha_inicio",
            "fecha_fin"
        ]


class PaymentStatus(str, Enum):
    """Estados de los pagos"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    REIMBURSED = "reimbursed"


class Payment(Document):
    """Modelo de pagos"""
    reservation_id: Optional[str] = None  # ObjectId como string
    user_id: Optional[str] = None  # ObjectId como string
    
    # Datos del pago
    amount: float
    method: str = Field(default="efectivo", max_length=50)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    
    # Información adicional
    transaction_id: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "payments"
        indexes = [
            "reservation_id",
            "user_id",
            "status",
            "created_at"
        ]


class SupportTicket(Document):
    """Modelo de tickets de soporte"""
    user_id: Optional[str] = None  # ObjectId como string
    reservation_id: Optional[str] = None  # ObjectId como string
    
    # Contenido del ticket
    subject: str = Field(..., max_length=200)
    message: str
    category: str = Field(default="general", max_length=50)
    priority: str = Field(default="medium", max_length=20)  # low, medium, high
    status: str = Field(default="abierto", max_length=50)  # abierto, cerrado
    
    # Respuesta admin
    admin_response: Optional[str] = None
    admin_user_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Settings:
        name = "support_tickets"
        indexes = [
            "user_id",
            "reservation_id",
            "status",
            "priority",
            "created_at"
        ]


class Newsletter(Document):
    """Alias para NewsletterSubscriber"""
    email: Indexed(EmailStr, unique=True)
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = Field(default=True)
    
    class Settings:
        name = "newsletter_subscribers"
        indexes = [
            "email",
            "active"
        ]
