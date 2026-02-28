from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db import get_db
from app.db_models import SavedPaymentMethod, User
from app.security import decode_access_token
from pydantic import BaseModel, Field, field_validator

router = APIRouter(prefix="/api/payment-methods", tags=["Payment Methods"])


# ========== Schemas ==========

class PaymentMethodCreate(BaseModel):
    card_type: str = Field(..., description="visa, mastercard, amex")
    card_holder: str = Field(..., min_length=3, max_length=120)
    card_last4: str = Field(..., min_length=4, max_length=4)
    expiry_month: str = Field(..., min_length=2, max_length=2)
    expiry_year: str = Field(..., min_length=4, max_length=4)
    is_default: bool = Field(default=False)

    @field_validator('card_type')
    @classmethod
    def validate_card_type(cls, value):
        allowed = {"visa", "mastercard", "amex"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("Tipo de tarjeta inválido")
        return normalized

    @field_validator('card_last4')
    @classmethod
    def validate_last4(cls, value):
        if not value.isdigit():
            raise ValueError("Los últimos 4 dígitos deben ser numéricos")
        return value

    @field_validator('expiry_month')
    @classmethod
    def validate_month(cls, value):
        if not value.isdigit() or not (1 <= int(value) <= 12):
            raise ValueError("Mes de expiración inválido")
        return value.zfill(2)

    @field_validator('expiry_year')
    @classmethod
    def validate_year(cls, value):
        if not value.isdigit() or len(value) != 4:
            raise ValueError("Año de expiración inválido")
        current_year = datetime.now().year
        if int(value) < current_year:
            raise ValueError("La tarjeta está vencida")
        return value


class PaymentMethodOut(BaseModel):
    id: int
    card_type: str
    card_holder: str
    card_last4: str
    expiry_month: str
    expiry_year: str
    is_default: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentMethodListOut(BaseModel):
    payment_methods: List[PaymentMethodOut]
    total: int


# ========== Dependency ==========

def get_current_user_from_token(request: Request, db: Session = Depends(get_db)) -> User:
    """Obtiene el usuario actual desde el token JWT"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticación requerido")
    
    token = auth.split(" ", 1)[1].strip()
    
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    email = (payload.get("sub") or "").lower().strip()
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return user


# ========== Endpoints ==========

@router.get("/", response_model=PaymentMethodListOut)
def list_payment_methods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Listar métodos de pago del usuario"""
    payment_methods = db.query(SavedPaymentMethod).filter(
        SavedPaymentMethod.user_id == current_user.id,
        SavedPaymentMethod.is_active == True
    ).order_by(SavedPaymentMethod.is_default.desc(), SavedPaymentMethod.created_at.desc()).all()
    
    return PaymentMethodListOut(
        payment_methods=payment_methods,
        total=len(payment_methods)
    )


@router.post("/", response_model=PaymentMethodOut, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payload: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Crear un nuevo método de pago"""
    
    # Si se marca como predeterminado, quitar el predeterminado actual
    if payload.is_default:
        db.query(SavedPaymentMethod).filter(
            SavedPaymentMethod.user_id == current_user.id,
            SavedPaymentMethod.is_default == True
        ).update({"is_default": False})
    
    payment_method = SavedPaymentMethod(
        user_id=current_user.id,
        card_type=payload.card_type,
        card_holder=payload.card_holder,
        card_last4=payload.card_last4,
        expiry_month=payload.expiry_month,
        expiry_year=payload.expiry_year,
        is_default=payload.is_default
    )
    
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    
    return payment_method


@router.put("/{payment_method_id}/set-default", response_model=PaymentMethodOut)
def set_default_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Establecer un método de pago como predeterminado"""
    
    payment_method = db.query(SavedPaymentMethod).filter(
        SavedPaymentMethod.id == payment_method_id,
        SavedPaymentMethod.user_id == current_user.id,
        SavedPaymentMethod.is_active == True
    ).first()
    
    if not payment_method:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    
    # Quitar predeterminado de todos los demás
    db.query(SavedPaymentMethod).filter(
        SavedPaymentMethod.user_id == current_user.id,
        SavedPaymentMethod.is_default == True
    ).update({"is_default": False})
    
    # Establecer este como predeterminado
    payment_method.is_default = True
    db.commit()
    db.refresh(payment_method)
    
    return payment_method


@router.delete("/{payment_method_id}", status_code=status.HTTP_200_OK)
def delete_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Eliminar un método de pago"""
    
    payment_method = db.query(SavedPaymentMethod).filter(
        SavedPaymentMethod.id == payment_method_id,
        SavedPaymentMethod.user_id == current_user.id
    ).first()
    
    if not payment_method:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    
    # Soft delete
    payment_method.is_active = False
    db.commit()
    
    return {"message": "Método de pago eliminado exitosamente", "id": payment_method_id}
