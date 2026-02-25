from fastapi import APIRouter, HTTPException
from app.models.schemas import Review, ReviewCreate, ReviewsResponse
from app.mongodb_models import Review as ReviewModel
from datetime import datetime
from typing import List

router = APIRouter()


@router.get("/", response_model=ReviewsResponse)
async def get_reviews(limit: int = 10):
    """
    Endpoint para obtener todas las calificaciones y reviews de usuarios
    
    - **limit**: Número máximo de reviews a retornar (default: 10)
    """
    try:
        # Obtener reviews ordenadas por fecha
        reviews_list = await ReviewModel.find().sort("-fecha").limit(limit).to_list()
        
        # Calcular promedio de calificación
        all_reviews = await ReviewModel.find_all().to_list()
        promedio = sum(r.calificacion for r in all_reviews) / len(all_reviews) if all_reviews else 0
        
        reviews_out = []
        for r in reviews_list:
            reviews_out.append(Review(
                id=str(r.id),
                usuario=r.usuario,
                calificacion=r.calificacion,
                comentario=r.comentario,
                fecha=r.fecha.date() if isinstance(r.fecha, datetime) else r.fecha
            ))
        
        return ReviewsResponse(
            reviews=reviews_out,
            promedio_calificacion=round(promedio, 2),
            total_reviews=len(all_reviews)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reviews: {str(e)}")


@router.post("/", response_model=Review)
async def create_review(review: ReviewCreate):
    """
    Endpoint para crear una nueva review
    
    - **usuario**: Nombre del usuario
    - **calificacion**: Calificación de 1 a 5
    - **comentario**: Comentario del usuario
    """
    try:
        # Crear nueva review
        new_review = ReviewModel(
            usuario=review.usuario,
            calificacion=review.calificacion,
            comentario=review.comentario,
            fecha=datetime.utcnow()
        )
        
        await new_review.insert()
        
        return Review(
            id=str(new_review.id),
            usuario=new_review.usuario,
            calificacion=new_review.calificacion,
            comentario=new_review.comentario,
            fecha=new_review.fecha.date()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear review: {str(e)}")


@router.get("/average")
async def get_average_rating():
    """
    Endpoint para obtener la calificación promedio
    """
    try:
        all_reviews = await ReviewModel.find_all().to_list()
        promedio = sum(r.calificacion for r in all_reviews) / len(all_reviews) if all_reviews else 0
        
        return {
            "promedio_calificacion": round(promedio, 2),
            "total_reviews": len(all_reviews)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular promedio: {str(e)}")
