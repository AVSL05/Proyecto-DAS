from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from app.db import get_db
from app.db_models import Invoice, Payment, Reservation, User, Vehicle
from app.routes.promotions import promotions_db
from app.schemas_reservations import (
    ReservationCreate, ReservationUpdate, ReservationOut, ReservationListOut, ReservationStats
)
from app.security import decode_access_token

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


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


def check_vehicle_availability(
    vehicle_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session,
    exclude_reservation_id: Optional[int] = None
) -> bool:
    """Verifica si un vehículo está disponible en las fechas especificadas"""
    
    # Verificar que el vehículo existe y está activo
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.is_active == True
    ).first()
    
    if not vehicle:
        return False
    
    # Buscar reservaciones que se traslapen con las fechas solicitadas
    query = db.query(Reservation).filter(
        Reservation.vehicle_id == vehicle_id,
        Reservation.status.in_(['pending', 'confirmed', 'in_progress']),
        or_(
            # La reservación existente empieza durante el período solicitado
            and_(
                Reservation.start_date >= start_date,
                Reservation.start_date < end_date
            ),
            # La reservación existente termina durante el período solicitado
            and_(
                Reservation.end_date > start_date,
                Reservation.end_date <= end_date
            ),
            # La reservación existente engloba el período solicitado
            and_(
                Reservation.start_date <= start_date,
                Reservation.end_date >= end_date
            )
        )
    )
    
    # Excluir una reservación específica (para actualizaciones)
    if exclude_reservation_id:
        query = query.filter(Reservation.id != exclude_reservation_id)
    
    conflicting_reservations = query.count()
    
    return conflicting_reservations == 0


def calculate_reservation_price(vehicle: Vehicle, start_date: datetime, end_date: datetime) -> tuple:
    """Calcula el precio total de la reservación"""
    delta = end_date - start_date
    total_days = max(1, delta.days)  # Mínimo 1 día
    
    price_per_day = vehicle.price_per_day
    total_price = price_per_day * total_days
    
    return total_days, price_per_day, total_price


def get_active_promotion(promotion_id: Optional[int]) -> Optional[dict]:
    if not promotion_id:
        return None

    today = date.today()
    promotion = next((promo for promo in promotions_db if promo["id"] == promotion_id), None)
    if not promotion:
        raise HTTPException(status_code=404, detail="Promocion no encontrada")

    is_active = bool(promotion.get("activa"))
    starts = promotion.get("fecha_inicio")
    ends = promotion.get("fecha_fin")
    if not is_active or starts is None or ends is None or not (starts <= today <= ends):
        raise HTTPException(status_code=400, detail="Promocion no vigente")

    return promotion


def build_reservation_folio(reservation_id: int) -> str:
    return f"VT-{reservation_id:04d}"


def build_invoice_number(reservation_id: int, issued_at: datetime) -> str:
    return f"FAC-{issued_at.strftime('%Y%m%d')}-{reservation_id:06d}"


@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Crear una nueva reservación"""
    
    # Verificar que el vehículo existe
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == payload.vehicle_id,
        Vehicle.is_active == True
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado o no disponible")
    
    # Verificar que las fechas sean futuras
    now = datetime.now(timezone.utc)
    if payload.start_date < now:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser futura")
    
    # Verificar disponibilidad
    if not check_vehicle_availability(payload.vehicle_id, payload.start_date, payload.end_date, db):
        raise HTTPException(
            status_code=409,
            detail="El vehículo no está disponible en las fechas seleccionadas"
        )
    
    # Calcular precios
    total_days, price_per_day, total_price = calculate_reservation_price(
        vehicle, payload.start_date, payload.end_date
    )

    promotion = get_active_promotion(payload.promotion_id)
    promotion_note = None
    if promotion:
        discount_percent = Decimal(str(promotion.get("descuento", 0)))
        discount_ratio = discount_percent / Decimal("100")
        discount_amount = (total_price * discount_ratio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_price = (total_price - discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if total_price < 0:
            total_price = Decimal("0.00")
        promotion_note = f"Promocion aplicada: {promotion['titulo']} ({promotion['descuento']}% OFF)"

    final_notes_parts = []
    if payload.notes:
        final_notes_parts.append(payload.notes.strip())
    if promotion_note:
        final_notes_parts.append(promotion_note)
    final_notes = " | ".join([part for part in final_notes_parts if part]) or None

    payment_method = (payload.payment_method or "efectivo").strip().lower()
    payment_reference = (payload.payment_reference or "").strip() or None
    payment_notes = (payload.payment_notes or "").strip() or None

    # Crear reservacion y pago en una sola transaccion
    reservation = Reservation(
        user_id=current_user.id,
        vehicle_id=payload.vehicle_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        pickup_location=payload.pickup_location,
        return_location=payload.return_location or payload.pickup_location,
        total_days=total_days,
        price_per_day=price_per_day,
        total_price=total_price,
        status='pending',
        notes=final_notes
    )

    db.add(reservation)
    db.flush()

    payment = Payment(
        reservation_id=reservation.id,
        user_id=current_user.id,
        method=payment_method,
        amount=total_price,
        status="accepted",
        reference=payment_reference,
        details=payment_notes,
    )

    db.add(payment)
    issued_at = datetime.now(timezone.utc)
    invoice = Invoice(
        reservation_id=reservation.id,
        folio=build_reservation_folio(reservation.id),
        invoice_number=build_invoice_number(reservation.id, issued_at),
        amount=total_price,
        currency="MXN",
        status="generated",
        issued_at=issued_at,
    )
    db.add(invoice)
    db.commit()
    db.refresh(reservation)
    
    # Agregar información del vehículo
    reservation.vehicle = vehicle
    reservation.user_name = current_user.full_name
    reservation.invoice_folio = invoice.folio
    reservation.invoice_number = invoice.invoice_number
    reservation.invoice_status = invoice.status
    reservation.invoice_issued_at = invoice.issued_at
    
    return reservation


@router.get("/{reservation_id}/invoice")
def get_invoice_for_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation or reservation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")

    invoice = db.query(Invoice).filter(Invoice.reservation_id == reservation.id).first()
    if not invoice:
        issued_at = datetime.now(timezone.utc)
        invoice = Invoice(
            reservation_id=reservation.id,
            folio=build_reservation_folio(reservation.id),
            invoice_number=build_invoice_number(reservation.id, issued_at),
            amount=reservation.total_price,
            currency="MXN",
            status="generated",
            issued_at=issued_at,
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)

    return {
        "reservation_id": reservation.id,
        "folio": invoice.folio,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
        "issued_at": invoice.issued_at,
        "amount": invoice.amount,
        "currency": invoice.currency,
    }


@router.get("/", response_model=ReservationListOut)
def list_my_reservations(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Listar todas las reservaciones del usuario actual"""
    
    query = db.query(Reservation).filter(Reservation.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Reservation.status == status_filter)
    
    total = query.count()
    reservations = query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()
    
    # Agregar información del vehículo, usuario e invoice
    for reservation in reservations:
        reservation.vehicle = db.query(Vehicle).filter(Vehicle.id == reservation.vehicle_id).first()
        reservation.user_name = current_user.full_name
        
        # Agregar información de la factura si existe
        invoice = db.query(Invoice).filter(Invoice.reservation_id == reservation.id).first()
        if invoice:
            reservation.invoice_folio = invoice.folio
            reservation.invoice_number = invoice.invoice_number
            reservation.invoice_status = invoice.status
            reservation.invoice_issued_at = invoice.issued_at
    
    return ReservationListOut(reservations=reservations, total=total)


@router.get("/stats", response_model=ReservationStats)
def get_my_reservation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Obtener estadísticas de reservaciones del usuario"""
    
    reservations = db.query(Reservation).filter(Reservation.user_id == current_user.id).all()
    
    total_reservations = len(reservations)
    active_reservations = sum(1 for r in reservations if r.status in ['pending', 'confirmed', 'in_progress'])
    completed_reservations = sum(1 for r in reservations if r.status == 'completed')
    cancelled_reservations = sum(1 for r in reservations if r.status == 'cancelled')
    total_spent = sum(r.total_price for r in reservations if r.status in ['completed', 'in_progress'])
    
    return ReservationStats(
        total_reservations=total_reservations,
        active_reservations=active_reservations,
        completed_reservations=completed_reservations,
        cancelled_reservations=cancelled_reservations,
        total_spent=total_spent
    )


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Obtener detalles de una reservación específica"""
    
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.user_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    # Agregar información del vehículo
    reservation.vehicle = db.query(Vehicle).filter(Vehicle.id == reservation.vehicle_id).first()
    reservation.user_name = current_user.full_name
    
    return reservation


@router.put("/{reservation_id}", response_model=ReservationOut)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Actualizar una reservación (solo si está pendiente)"""
    
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.user_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    if reservation.status not in ['pending']:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden modificar reservaciones pendientes"
        )
    
    # Actualizar fechas si se proporcionan
    if payload.start_date or payload.end_date:
        new_start = payload.start_date or reservation.start_date
        new_end = payload.end_date or reservation.end_date
        
        # Verificar disponibilidad con las nuevas fechas
        if not check_vehicle_availability(
            reservation.vehicle_id, new_start, new_end, db, exclude_reservation_id=reservation_id
        ):
            raise HTTPException(
                status_code=409,
                detail="El vehículo no está disponible en las nuevas fechas"
            )
        
        # Recalcular precios
        vehicle = db.query(Vehicle).filter(Vehicle.id == reservation.vehicle_id).first()
        total_days, price_per_day, total_price = calculate_reservation_price(vehicle, new_start, new_end)
        
        reservation.start_date = new_start
        reservation.end_date = new_end
        reservation.total_days = total_days
        reservation.total_price = total_price
    
    # Actualizar otros campos
    if payload.pickup_location:
        reservation.pickup_location = payload.pickup_location
    if payload.return_location:
        reservation.return_location = payload.return_location
    if payload.notes is not None:
        reservation.notes = payload.notes
    
    db.commit()
    db.refresh(reservation)
    
    # Agregar información del vehículo
    reservation.vehicle = db.query(Vehicle).filter(Vehicle.id == reservation.vehicle_id).first()
    reservation.user_name = current_user.full_name
    
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_200_OK)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Cancelar una reservación"""
    
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.user_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    if reservation.status in ['completed', 'cancelled']:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede cancelar una reservación {reservation.status}"
        )
    
    reservation.status = 'cancelled'
    reservation.cancelled_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"message": "Reservación cancelada exitosamente", "reservation_id": reservation_id}

