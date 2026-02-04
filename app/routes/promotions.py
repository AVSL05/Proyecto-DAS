from fastapi import APIRouter, HTTPException
from app.models.schemas import Promotion
from datetime import date
from typing import List

router = APIRouter()

# Base de datos simulada de promociones
promotions_db = [
    {
        "id": 1,
        "titulo": "Promocion 1",
        "descripcion": "Descuento especial para viajes en febrero. ¡Aprovecha esta increíble oferta!",
        "descuento": 15.0,
        "imagen_url": "/images/promo1.jpg",
        "fecha_inicio": date(2026, 2, 1),
        "fecha_fin": date(2026, 2, 28),
        "activa": True
    },
    {
        "id": 2,
        "titulo": "Promocion 2",
        "descripcion": "Viajes de fin de semana con 20% de descuento. ¡No te lo pierdas!",
        "descuento": 20.0,
        "imagen_url": "/images/promo2.jpg",
        "fecha_inicio": date(2026, 2, 1),
        "fecha_fin": date(2026, 3, 31),
        "activa": True
    },
    {
        "id": 3,
        "titulo": "Promocion 3",
        "descripcion": "Reserva anticipada y ahorra hasta 25%. ¡Planifica tu viaje con tiempo!",
        "descuento": 25.0,
        "imagen_url": "/images/promo3.jpg",
        "fecha_inicio": date(2026, 2, 1),
        "fecha_fin": date(2026, 4, 30),
        "activa": True
    }
]

@router.get("/", response_model=List[Promotion])
async def get_promotions(activa: bool = True):
    """
    Endpoint para obtener todas las promociones activas
    
    - **activa**: Filtrar por promociones activas (default: True)
    """
    try:
        if activa:
            # Filtrar solo promociones activas y vigentes
            today = date.today()
            promociones = [
                Promotion(**promo) for promo in promotions_db
                if promo["activa"] and promo["fecha_inicio"] <= today <= promo["fecha_fin"]
            ]
        else:
            promociones = [Promotion(**promo) for promo in promotions_db]
        
        return promociones
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener promociones: {str(e)}")

@router.get("/{promotion_id}", response_model=Promotion)
async def get_promotion_by_id(promotion_id: int):
    """
    Endpoint para obtener una promoción específica por ID
    
    - **promotion_id**: ID de la promoción
    """
    promo = next((p for p in promotions_db if p["id"] == promotion_id), None)
    
    if not promo:
        raise HTTPException(status_code=404, detail=f"Promoción con ID {promotion_id} no encontrada")
    
    return Promotion(**promo)
