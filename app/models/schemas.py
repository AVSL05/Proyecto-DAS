from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List
from enum import Enum

# Modelos para búsqueda de transporte
class TransportSearchRequest(BaseModel):
    origen: str = Field(..., description="Ubicación de origen")
    destino: str = Field(..., description="Ubicación de destino")
    fecha_salida: date = Field(..., description="Fecha de salida")
    num_pasajeros: int = Field(..., ge=1, le=50, description="Número de pasajeros")

class TransportType(str, Enum):
    BUS = "bus"
    VAN = "van"
    MINIBUS = "minibus"
    AUTOBUS = "autobus"

class TransportResult(BaseModel):
    id: int
    tipo: TransportType
    origen: str
    destino: str
    fecha_salida: date
    hora_salida: str
    capacidad: int
    precio: float
    disponible: bool
    empresa: str

class SearchResponse(BaseModel):
    resultados: List[TransportResult]
    total: int

# Modelos para promociones
class Promotion(BaseModel):
    id: int
    titulo: str
    descripcion: str
    descuento: float = Field(..., ge=0, le=100, description="Porcentaje de descuento")
    imagen_url: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date
    activa: bool

# Modelos para reviews/calificaciones
class ReviewCreate(BaseModel):
    usuario: str = Field(..., min_length=2, max_length=100)
    calificacion: int = Field(..., ge=1, le=5, description="Calificación de 1 a 5")
    comentario: str = Field(..., min_length=10, max_length=500)

class Review(BaseModel):
    id: int
    usuario: str
    calificacion: int
    comentario: str
    fecha: date
    
class ReviewsResponse(BaseModel):
    reviews: List[Review]
    promedio_calificacion: float
    total_reviews: int

# Modelos para newsletter
class NewsletterSubscribe(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico para suscripción")

class NewsletterResponse(BaseModel):
    success: bool
    message: str
    email: str
