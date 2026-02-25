from fastapi import APIRouter, HTTPException
from app.models.schemas import Promotion
from app.mongodb_models import Promotion as PromotionModel
from datetime import datetime
from typing import List

router = APIRouter()


@router.get("/", response_model=List[Promotion])
async def get_promotions(activa: bool = True):
    """
    Endpoint para obtener todas las promociones activas
    
    - **activa**: Filtrar por promociones activas (default: True)
    """
    try:
        filters = {}
        if activa:
            filters["activa"] = True
            # También filtrar por fecha vigente
            now = datetime.utcnow()
            filters["fecha_inicio"] = {"$lte": now}
            filters["fecha_fin"] = {"$gte": now}
        
        promotions = await PromotionModel.find(filters).sort("+fecha_inicio").to_list()
        
        promotions_out = []
        for p in promotions:
            promotions_out.append(Promotion(
                id=str(p.id),
                titulo=p.titulo,
                descripcion=p.descripcion,
                descuento=p.descuento,
                imagen_url=p.imagen_url,
                fecha_inicio=p.fecha_inicio.date() if isinstance(p.fecha_inicio, datetime) else p.fecha_inicio,
                fecha_fin=p.fecha_fin.date() if isinstance(p.fecha_fin, datetime) else p.fecha_fin,
                activa=p.activa
            ))
        
        return promotions_out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener promociones: {str(e)}")


@router.get("/{promo_id}", response_model=Promotion)
async def get_promotion(promo_id: str):
    """
    Endpoint para obtener una promoción específica
    
    - **promo_id**: ID de la promoción
    """
    try:
        from beanie import PydanticObjectId
        promotion = await PromotionModel.get(PydanticObjectId(promo_id))
        
        if not promotion:
            raise HTTPException(status_code=404, detail="Promoción no encontrada")
        
        return Promotion(
            id=str(promotion.id),
            titulo=promotion.titulo,
            descripcion=promotion.descripcion,
            descuento=promotion.descuento,
            imagen_url=promotion.imagen_url,
            fecha_inicio=promotion.fecha_inicio.date() if isinstance(promotion.fecha_inicio, datetime) else promotion.fecha_inicio,
            fecha_fin=promotion.fecha_fin.date() if isinstance(promotion.fecha_fin, datetime) else promotion.fecha_fin,
            activa=promotion.activa
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")


@router.post("/", response_model=Promotion)
async def create_promotion(promotion_data: dict):
    """
    Endpoint para crear una nueva promoción (uso administrativo)
    """
    try:
        new_promotion = PromotionModel(
            titulo=promotion_data["titulo"],
            descripcion=promotion_data["descripcion"],
            descuento=promotion_data["descuento"],
            imagen_url=promotion_data.get("imagen_url"),
            fecha_inicio=datetime.fromisoformat(promotion_data["fecha_inicio"]),
            fecha_fin=datetime.fromisoformat(promotion_data["fecha_fin"]),
            activa=promotion_data.get("activa", True)
        )
        
        await new_promotion.insert()
        
        return Promotion(
            id=str(new_promotion.id),
            titulo=new_promotion.titulo,
            descripcion=new_promotion.descripcion,
            descuento=new_promotion.descuento,
            imagen_url=new_promotion.imagen_url,
            fecha_inicio=new_promotion.fecha_inicio.date(),
            fecha_fin=new_promotion.fecha_fin.date(),
            activa=new_promotion.activa
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear promoción: {str(e)}")
