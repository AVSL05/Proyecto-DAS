from fastapi import APIRouter, HTTPException
from app.models.schemas import NewsletterSubscribe, NewsletterResponse
from typing import List

router = APIRouter()

# Base de datos simulada de suscriptores
newsletter_subscribers = []

@router.post("/subscribe", response_model=NewsletterResponse)
async def subscribe_newsletter(subscription: NewsletterSubscribe):
    """
    Endpoint para suscribirse al boletín de ofertas especiales
    
    - **email**: Correo electrónico del suscriptor
    """
    try:
        # Verificar si el email ya está suscrito
        if subscription.email in newsletter_subscribers:
            return NewsletterResponse(
                success=False,
                message="Este correo ya está suscrito a nuestro boletín",
                email=subscription.email
            )
        
        # Agregar nuevo suscriptor
        newsletter_subscribers.append(subscription.email)
        
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
    return {
        "suscriptores": newsletter_subscribers,
        "total": len(newsletter_subscribers)
    }

@router.delete("/unsubscribe/{email}")
async def unsubscribe_newsletter(email: str):
    """
    Endpoint para darse de baja del boletín
    
    - **email**: Correo electrónico a dar de baja
    """
    if email not in newsletter_subscribers:
        raise HTTPException(status_code=404, detail="Email no encontrado en la lista de suscriptores")
    
    newsletter_subscribers.remove(email)
    
    return {
        "success": True,
        "message": f"El correo {email} ha sido dado de baja del boletín",
        "email": email
    }
