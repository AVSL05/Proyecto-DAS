from fastapi import APIRouter, HTTPException, status, Request, Query
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from beanie import PydanticObjectId

from app.mongodb_models import Reservation, Vehicle, User, ReservationStatus
from app.schemas_reservations_mongo import (
    ReservationCreate, ReservationUpdate, ReservationOut, ReservationListOut, ReservationStats, VehicleOut
)
from app.security import decode_access_token

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


async def get_current_user_from_token(request: Request) -> User:
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
    
    user = await User.find_one(User.email == email)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return user


async def check_vehicle_availability(
    vehicle_id: str,
    start_date: datetime,
    end_date: datetime,
    exclude_reservation_id: Optional[str] = None
) -> bool:
    """Verifica si un vehículo está disponible en las fechas especificadas"""
    
    # Verificar que el vehículo existe y está activo
    try:
        vehicle = await Vehicle.get(PydanticObjectId(vehicle_id))
    except Exception:
        return False
    
    if not vehicle or not vehicle.is_active:
        return False
    
    # Buscar reservaciones que se traslapen con las fechas solicitadas
    filters = {
        "vehicle_id": vehicle_id,
        "status": {"$in": ["pending", "confirmed", "in_progress"]},
        "$or": [
            # La reservación existente empieza durante el período solicitado
            {"start_date": {"$gte": start_date, "$lt": end_date}},
            # La reservación existente termina durante el período solicitado
            {"end_date": {"$gt": start_date, "$lte": end_date}},
            # La reservación existente engloba el período solicitado
            {"start_date": {"$lte": start_date}, "end_date": {"$gte": end_date}}
        ]
    }
    
    reservations = await Reservation.find(filters).to_list()
    
    # Excluir una reservación específica (para actualizaciones)
    if exclude_reservation_id:
        reservations = [r for r in reservations if str(r.id) != exclude_reservation_id]
    
    return len(reservations) == 0


def calculate_reservation_price(vehicle: Vehicle, start_date: datetime, end_date: datetime) -> tuple:
    """Calcula el precio total de la reservación"""
    delta = end_date - start_date
    total_days = max(1, delta.days)  # Mínimo 1 día
    
    price_per_day = vehicle.price_per_day
    total_price = price_per_day * total_days
    
    return total_days, price_per_day, total_price


@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    payload: ReservationCreate,
    request: Request
):
    """Crear una nueva reservación"""
    
    current_user = await get_current_user_from_token(request)
    
    # Verificar que el vehículo existe
    try:
        vehicle = await Vehicle.get(PydanticObjectId(payload.vehicle_id))
    except Exception:
        raise HTTPException(status_code=400, detail="ID de vehículo inválido")
    
    if not vehicle or not vehicle.is_active:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado o no disponible")
    
    # Verificar que las fechas sean futuras
    now = datetime.now(timezone.utc)
    if payload.start_date < now:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser futura")
    
    # Verificar disponibilidad
    if not await check_vehicle_availability(payload.vehicle_id, payload.start_date, payload.end_date):
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
        user_id=str(current_user.id),
        vehicle_id=payload.vehicle_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        pickup_location=payload.pickup_location,
        return_location=payload.return_location or payload.pickup_location,
        total_days=total_days,
        price_per_day=price_per_day,
        total_price=total_price,
        status=ReservationStatus.PENDING,
        notes=payload.notes
    )
    
    await reservation.insert()
    
    # Construir respuesta
    vehicle_dict = vehicle.dict()
    vehicle_dict["id"] = str(vehicle.id)
    
    reservation_dict = reservation.dict()
    reservation_dict["id"] = str(reservation.id)
    reservation_dict["vehicle"] = VehicleOut(**vehicle_dict)
    reservation_dict["user_name"] = current_user.full_name
    
    return ReservationOut(**reservation_dict)


@router.get("/", response_model=ReservationListOut)
async def list_my_reservations(
    request: Request,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """Listar todas las reservaciones del usuario actual"""
    
    current_user = await get_current_user_from_token(request)
    
    filters = {"user_id": str(current_user.id)}
    
    if status_filter:
        filters["status"] = status_filter
    
    total = await Reservation.find(filters).count()
    reservations = await Reservation.find(filters).sort("-created_at").skip(skip).limit(limit).to_list()
    
    # Agregar información del vehículo
    reservations_out = []
    for reservation in reservations:
        try:
            vehicle = await Vehicle.get(PydanticObjectId(reservation.vehicle_id))
            vehicle_dict = vehicle.dict()
            vehicle_dict["id"] = str(vehicle.id)
            
            reservation_dict = reservation.dict()
            reservation_dict["id"] = str(reservation.id)
            reservation_dict["vehicle"] = VehicleOut(**vehicle_dict)
            reservation_dict["user_name"] = current_user.full_name
            
            reservations_out.append(ReservationOut(**reservation_dict))
        except Exception:
            # Si no se encuentra el vehículo, omitir esta reservación
            continue
    
    return ReservationListOut(reservations=reservations_out, total=total)


@router.get("/stats", response_model=ReservationStats)
async def get_my_reservation_stats(request: Request):
    """Obtener estadísticas de reservaciones del usuario"""
    
    current_user = await get_current_user_from_token(request)
    
    reservations = await Reservation.find({"user_id": str(current_user.id)}).to_list()
    
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
async def get_reservation(
    reservation_id: str,
    request: Request
):
    """Obtener detalles de una reservación específica"""
    
    current_user = await get_current_user_from_token(request)
    
    try:
        reservation = await Reservation.get(PydanticObjectId(reservation_id))
    except Exception:
        raise HTTPException(status_code=400, detail="ID de reservación inválido")
    
    if not reservation or reservation.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    # Agregar información del vehículo
    vehicle = await Vehicle.get(PydanticObjectId(reservation.vehicle_id))
    vehicle_dict = vehicle.dict()
    vehicle_dict["id"] = str(vehicle.id)
    
    reservation_dict = reservation.dict()
    reservation_dict["id"] = str(reservation.id)
    reservation_dict["vehicle"] = VehicleOut(**vehicle_dict)
    reservation_dict["user_name"] = current_user.full_name
    
    return ReservationOut(**reservation_dict)


@router.put("/{reservation_id}", response_model=ReservationOut)
async def update_reservation(
    reservation_id: str,
    payload: ReservationUpdate,
    request: Request
):
    """Actualizar una reservación (solo si está pendiente)"""
    
    current_user = await get_current_user_from_token(request)
    
    try:
        reservation = await Reservation.get(PydanticObjectId(reservation_id))
    except Exception:
        raise HTTPException(status_code=400, detail="ID de reservación inválido")
    
    if not reservation or reservation.user_id != str(current_user.id):
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
        if not await check_vehicle_availability(
            reservation.vehicle_id, new_start, new_end, exclude_reservation_id=reservation_id
        ):
            raise HTTPException(
                status_code=409,
                detail="El vehículo no está disponible en las nuevas fechas"
            )
        
        # Recalcular precios
        vehicle = await Vehicle.get(PydanticObjectId(reservation.vehicle_id))
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
    
    reservation.updated_at = datetime.now(timezone.utc)
    await reservation.save()
    
    # Agregar información del vehículo
    vehicle = await Vehicle.get(PydanticObjectId(reservation.vehicle_id))
    vehicle_dict = vehicle.dict()
    vehicle_dict["id"] = str(vehicle.id)
    
    reservation_dict = reservation.dict()
    reservation_dict["id"] = str(reservation.id)
    reservation_dict["vehicle"] = VehicleOut(**vehicle_dict)
    reservation_dict["user_name"] = current_user.full_name
    
    return ReservationOut(**reservation_dict)


@router.delete("/{reservation_id}", status_code=status.HTTP_200_OK)
async def cancel_reservation(
    reservation_id: str,
    request: Request
):
    """Cancelar una reservación"""
    
    current_user = await get_current_user_from_token(request)
    
    try:
        reservation = await Reservation.get(PydanticObjectId(reservation_id))
    except Exception:
        raise HTTPException(status_code=400, detail="ID de reservación inválido")
    
    if not reservation or reservation.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    if reservation.status in ['completed', 'cancelled']:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede cancelar una reservación {reservation.status}"
        )
    
    reservation.status = ReservationStatus.CANCELLED
    reservation.cancelled_at = datetime.now(timezone.utc)
    await reservation.save()
    
    return {"message": "Reservación cancelada exitosamente", "reservation_id": reservation_id}
