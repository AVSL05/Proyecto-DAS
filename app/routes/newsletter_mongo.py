from fastapi import APIRouter, HTTPException
from app.models.schemas import NewsletterSubscribe, NewsletterResponse
from app.mongodb_models import NewsletterSubscriber
from typing import List

router = APIRouter()


@router.post("/subscribe", response_model=NewsletterResponse)
async def subscribe_newsletter(subscription: NewsletterSubscribe):
    """
    Endpoint para suscribirse al boletín de ofertas especiales
    
    - **email**: Correo electrónico del suscriptor
    """
    try:
        # Verificar si el email ya está suscrito
        existing = await NewsletterSubscriber.find_one(
            NewsletterSubscriber.email == subscription.email
        )
        
        if existing and existing.active:
            return NewsletterResponse(
                success=False,
                message="Este correo ya está suscrito a nuestro boletín",
                email=subscription.email
            )
        
        if existing and not existing.active:
            # Reactivar suscripción
            existing.active = True
            await existing.save()
        else:
            # Agregar nuevo suscriptor
            new_subscriber = NewsletterSubscriber(email=subscription.email)
            await new_subscriber.insert()
        
        return NewsletterResponse(
            success=True,
            message="¡Gracias por suscribirte! Recibirás nuestras ofertas especiales en tu correo.",
            email=subscription.email
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al suscribir: {str(e)}")


@router.get("/subscribers")
async def get_subscribers():
    """
    Endpoint para obtener la lista de suscriptores (uso administrativo)
    """
    try:
        subscribers = await NewsletterSubscriber.find(
            NewsletterSubscriber.active == True
        ).to_list()
        
        return {
            "suscriptores": [s.email for s in subscribers],
            "total": len(subscribers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener suscriptores: {str(e)}")


@router.delete("/unsubscribe/{email}")
async def unsubscribe_newsletter(email: str):
    """
    Endpoint para darse de baja del boletín
    
    - **email**: Correo electrónico a dar de baja
    """
    try:
        subscriber = await NewsletterSubscriber.find_one(
            NewsletterSubscriber.email == email
        )
        
        if not subscriber or not subscriber.active:
            return {
                "success": False,
                "message": "El correo no está suscrito a nuestro boletín"
            }
        
        # Marcar como inactivo en lugar de eliminar
        subscriber.active = False
        await subscriber.save()
        
        return {
            "success": True,
            "message": "Te has dado de baja exitosamente del boletín"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al dar de baja: {str(e)}")
