from sqlalchemy import Column, Integer, String, DateTime, func, Numeric, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from .db import Base
from sqlalchemy import Boolean
import enum

class UserRole(str, enum.Enum):
    CLIENT = "cliente"
    ADMIN = "administrativo"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True)  # Nullable para usuarios de Google
    password_hash = Column(String(255), nullable=True)  # Nullable para OAuth
    google_id = Column(String(255), nullable=True, unique=True, index=True)  # ID de Google
    avatar_url = Column(String(500), nullable=True)  # URL de avatar de Google
    role = Column(
        String(30),
        nullable=False,
        default=UserRole.CLIENT.value,
        server_default=UserRole.CLIENT.value,
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relaciones
    reservations = relationship("Reservation", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token_hash = Column(String(64), unique=True, index=True, nullable=False)  # sha256 hex = 64 chars
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class VehicleType(str, enum.Enum):
    """Tipos de vehículos disponibles"""
    VAN = "van"
    PICKUP = "pickup"
    TRUCK = "truck"
    SUV = "suv"
    MINIBUS = "minibus"


class VehicleStatus(str, enum.Enum):
    """Estados del vehículo"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class Vehicle(Base):
    """Modelo de vehículos/transportes disponibles"""
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False)  # Marca (Toyota, Ford, etc)
    model = Column(String(100), nullable=False)  # Modelo (Hiace, F-150, etc)
    year = Column(Integer, nullable=False)  # Año del vehículo
    vehicle_type = Column(String(50), nullable=False)  # van, pickup, truck, etc
    capacity = Column(Integer, nullable=False)  # Capacidad de pasajeros
    plate = Column(String(20), unique=True, index=True, nullable=False)  # Placa
    color = Column(String(50), nullable=True)  # Color del vehículo
    
    # Precios
    price_per_day = Column(Numeric(10, 2), nullable=False)  # Precio por día
    price_per_hour = Column(Numeric(10, 2), nullable=True)  # Precio por hora (opcional)
    
    # Detalles
    description = Column(Text, nullable=True)  # Descripción del vehículo
    features = Column(Text, nullable=True)  # Características (JSON string: AC, GPS, etc)
    image_url = Column(String(500), nullable=True)  # URL de imagen
    
    # Estado
    status = Column(String(50), default="available", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)  # Si está disponible para rentar
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relaciones
    reservations = relationship("Reservation", back_populates="vehicle")


class ReservationStatus(str, enum.Enum):
    """Estados de la reservación"""
    PENDING = "pending"  # Pendiente de confirmación
    CONFIRMED = "confirmed"  # Confirmada
    IN_PROGRESS = "in_progress"  # En curso
    COMPLETED = "completed"  # Completada
    CANCELLED = "cancelled"  # Cancelada


class Reservation(Base):
    """Modelo de reservaciones"""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Referencias
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    
    # Fechas
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Detalles de la reservación
    pickup_location = Column(String(200), nullable=False)  # Lugar de recogida
    return_location = Column(String(200), nullable=True)  # Lugar de devolución (puede ser el mismo)
    
    # Precios
    total_days = Column(Integer, nullable=False)  # Días totales
    price_per_day = Column(Numeric(10, 2), nullable=False)  # Precio por día al momento de reservar
    total_price = Column(Numeric(10, 2), nullable=False)  # Precio total
    
    # Estado y notas
    status = Column(String(50), default="pending", nullable=False, index=True)
    notes = Column(Text, nullable=True)  # Notas adicionales del cliente
    admin_notes = Column(Text, nullable=True)  # Notas internas
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="reservations")
    vehicle = relationship("Vehicle", back_populates="reservations")
    payment = relationship("Payment", back_populates="reservation", uselist=False, cascade="all, delete-orphan")


class Payment(Base):
    """Modelo de pagos registrados para reservaciones."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    method = Column(String(30), nullable=False, default="efectivo", index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(8), nullable=False, default="MXN")
    status = Column(String(30), nullable=False, default="accepted", index=True)
    reference = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    reservation = relationship("Reservation", back_populates="payment")
    user = relationship("User", back_populates="payments")
