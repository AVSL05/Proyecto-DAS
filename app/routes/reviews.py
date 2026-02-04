from fastapi import APIRouter, HTTPException
from app.models.schemas import Review, ReviewCreate, ReviewsResponse
from datetime import date
from typing import List

router = APIRouter()

# Base de datos simulada de reviews
reviews_db = [
    {
        "id": 1,
        "usuario": "Miguel Martinez",
        "calificacion": 5,
        "comentario": "Excelente sevicio!!!",
        "fecha": date(2026, 1, 15)
    },
    {
        "id": 2,
        "usuario": "Ana García",
        "calificacion": 5,
        "comentario": "Muy puntual y cómodo. El conductor fue muy amable y profesional.",
        "fecha": date(2026, 1, 20)
    },
    {
        "id": 3,
        "usuario": "Carlos López",
        "calificacion": 4,
        "comentario": "Buen servicio en general. Los asientos son cómodos y el precio es justo.",
        "fecha": date(2026, 1, 25)
    }
]

@router.get("/", response_model=ReviewsResponse)
async def get_reviews(limit: int = 10):
    """
    Endpoint para obtener todas las calificaciones y reviews de usuarios
    
    - **limit**: Número máximo de reviews a retornar (default: 10)
    """
    try:
        # Ordenar por fecha más reciente
        reviews_sorted = sorted(reviews_db, key=lambda x: x["fecha"], reverse=True)
        reviews_limited = reviews_sorted[:limit]
        
        # Calcular promedio de calificación
        total_calificaciones = sum(r["calificacion"] for r in reviews_db)
        promedio = total_calificaciones / len(reviews_db) if reviews_db else 0
        
        return ReviewsResponse(
            reviews=[Review(**r) for r in reviews_limited],
            promedio_calificacion=round(promedio, 2),
            total_reviews=len(reviews_db)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reviews: {str(e)}")

@router.post("/", response_model=Review)
async def create_review(review: ReviewCreate):
    """
    Endpoint para crear una nueva calificación/review
    
    - **usuario**: Nombre del usuario
    - **calificacion**: Calificación de 1 a 5 estrellas
    - **comentario**: Comentario del usuario
    """
    try:
        # Generar nuevo ID
        new_id = max([r["id"] for r in reviews_db]) + 1 if reviews_db else 1
        
        # Crear nueva review
        new_review = {
            "id": new_id,
            "usuario": review.usuario,
            "calificacion": review.calificacion,
            "comentario": review.comentario,
            "fecha": date.today()
        }
        
        reviews_db.append(new_review)
        
        return Review(**new_review)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear review: {str(e)}")

@router.get("/average")
async def get_average_rating():
    """
    Endpoint para obtener el promedio de calificaciones
    """
    if not reviews_db:
        return {"promedio_calificacion": 0, "total_reviews": 0}
    
    total_calificaciones = sum(r["calificacion"] for r in reviews_db)
    promedio = total_calificaciones / len(reviews_db)
    
    return {
        "promedio_calificacion": round(promedio, 2),
        "total_reviews": len(reviews_db)
    }
