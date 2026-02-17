from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from app.db import get_db
from app.db_models import Reservation, Vehicle, User
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
    
    # Crear reservación
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
        notes=payload.notes
    )
    
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    
    # Agregar información del vehículo
    reservation.vehicle = vehicle
    reservation.user_name = current_user.full_name
    
    return reservation


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
    
    # Agregar información del vehículo y usuario
    for reservation in reservations:
        reservation.vehicle = db.query(Vehicle).filter(Vehicle.id == reservation.vehicle_id).first()
        reservation.user_name = current_user.full_name
    
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
