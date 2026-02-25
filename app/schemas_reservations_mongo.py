from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

# ===== Vehicle Schemas =====

class VehicleBase(BaseModel):
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    vehicle_type: str = Field(..., description="van, pickup, truck, suv, minibus")
    capacity: int = Field(..., ge=1, le=50)
    plate: str = Field(..., min_length=3, max_length=20)
    color: Optional[str] = None
    price_per_day: float = Field(..., ge=0)
    price_per_hour: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    features: Optional[str] = None  # JSON string
    image_url: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_type: Optional[str] = None
    capacity: Optional[int] = None
    plate: Optional[str] = None
    color: Optional[str] = None
    price_per_day: Optional[float] = None
    price_per_hour: Optional[float] = None
    description: Optional[str] = None
    features: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleOut(VehicleBase):
    id: str  # MongoDB usa string IDs
    status: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VehicleListOut(BaseModel):
    vehicles: List[VehicleOut]
    total: int


# ===== Reservation Schemas =====

class ReservationBase(BaseModel):
    vehicle_id: str  # MongoDB usa string IDs
    start_date: datetime
    end_date: datetime
    pickup_location: str = Field(..., min_length=3, max_length=200)
    return_location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, end_date, info):
        if 'start_date' in info.data:
            start_date = info.data['start_date']
            if end_date <= start_date:
                raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return end_date


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    pickup_location: Optional[str] = None
    return_location: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class ReservationOut(BaseModel):
    id: str  # MongoDB usa string IDs
    user_id: str
    vehicle_id: str
    start_date: datetime
    end_date: datetime
    pickup_location: str
    return_location: Optional[str]
    total_days: int
    price_per_day: float
    total_price: float
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    
    # Datos del vehículo incluidos
    vehicle: Optional[VehicleOut] = None
    
    # Datos del usuario (solo nombre)
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


class ReservationListOut(BaseModel):
    reservations: List[ReservationOut]
    total: int


class ReservationStats(BaseModel):
    """Estadísticas de reservaciones para el usuario"""
    total_reservations: int
    active_reservations: int
    completed_reservations: int
    cancelled_reservations: int
    total_spent: float
