"""
Router de administración para MongoDB
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from beanie import PydanticObjectId

from app.mongodb_models import User, UserRole, Vehicle, VehicleStatus, Reservation, ReservationStatus, Payment, PaymentStatus, SupportTicket, Newsletter
from app.security import decode_access_token

router = APIRouter(prefix="/api/admin", tags=["Admin"])

ALLOWED_RESERVATION_STATUS = {"pending", "confirmed", "in_progress", "completed", "cancelled"}
ALLOWED_VEHICLE_STATUS = {"available", "reserved", "in_use", "maintenance", "unavailable"}
VALID_ROLES = {UserRole.CLIENT.value, UserRole.ADMIN.value}
PAID_RESERVATION_STATUS = {"confirmed", "in_progress", "completed"}
ACCEPTED_PAYMENT_STATUS = {"accepted"}
REFUNDED_PAYMENT_STATUS = {"refunded", "reimbursed"}
ACTIVE_RESERVATION_STATUS = {"pending", "confirmed", "in_progress"}
PAYMENT_ALERT_RESERVATION_STATUS = {"pending"}
PAYMENT_ALERT_THRESHOLD_DAYS = 45
CRM_SLA_HOURS = 48


class AdminReservationUpdate(BaseModel):
    status: Optional[str] = Field(default=None)
    admin_notes: Optional[str] = Field(default=None, max_length=1500)


class AdminVehicleUpdate(BaseModel):
    status: Optional[str] = None
    is_active: Optional[bool] = None
    price_per_day: Optional[float] = Field(default=None, ge=0)
    price_per_hour: Optional[float] = Field(default=None, ge=0)


class AdminUserRoleUpdate(BaseModel):
    role: str


def to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def normalize_status(status: Optional[str]) -> str:
    return (status or "").strip().lower()


def normalize_case_status(status: Optional[str]) -> str:
    normalized = normalize_status(status)
    if normalized in {"open", "abierto", "pending", "pendiente"}:
        return "abierto"
    if normalized in {"closed", "cerrado", "resolved", "resuelto"}:
        return "cerrado"
    return normalized or "abierto"


def infer_refund_status(reservation_status: str, payment_status: str, is_paid: bool) -> str:
    if payment_status in REFUNDED_PAYMENT_STATUS:
        return "reembolsado"
    if reservation_status == "cancelled" and is_paid:
        return "pendiente"
    return "no_aplica"


def normalize_role(role: Optional[str]) -> str:
    role_value = (role or UserRole.CLIENT.value).strip().lower()
    if role_value not in VALID_ROLES:
        return UserRole.CLIENT.value
    return role_value


async def get_current_user_from_token(request: Request) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no válido")
    
    token = auth.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    # El email está en 'sub' (subject), no en 'email'
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = await User.find_one(User.email == email)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return user


async def require_admin(request: Request) -> User:
    user = await get_current_user_from_token(request)
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere rol administrativo.")
    return user


@router.get("/summary")
async def get_admin_summary(
    _: User = Depends(require_admin),
):
    """Obtener resumen general del panel administrativo"""
    now_utc = datetime.now(timezone.utc)
    alert_cutoff = now_utc - timedelta(days=PAYMENT_ALERT_THRESHOLD_DAYS)

    total_users = await User.count()
    total_admins = await User.find(User.role == UserRole.ADMIN).count()
    total_clients = total_users - total_admins

    total_reservations = await Reservation.count()
    pending_reservations = await Reservation.find(Reservation.status == ReservationStatus.PENDING).count()
    active_reservations = await Reservation.find(
        {"status": {"$in": ["pending", "confirmed", "in_progress"]}}
    ).count()

    total_vehicles = await Vehicle.count()
    active_vehicles = await Vehicle.find(Vehicle.is_active == True).count()
    
    # Alertas de pago
    payment_alerts_count = await Reservation.find(
        {
            "status": "pending",
            "created_at": {"$lte": alert_cutoff}
        }
    ).count()

    return {
        "users": {
            "total": total_users,
            "admins": total_admins,
            "clients": total_clients,
        },
        "reservations": {
            "total": total_reservations,
            "pending": pending_reservations,
            "active": active_reservations,
        },
        "vehicles": {
            "total": total_vehicles,
            "active": active_vehicles,
        },
        "alerts": {
            "payment_overdue": payment_alerts_count,
        },
    }


@router.get("/sales")
async def get_admin_sales(
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(require_admin),
):
    """Obtener información de ventas y transacciones"""
    now_utc = datetime.now(timezone.utc)
    day_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = day_start.replace(day=1)

    all_payments = await Payment.find_all().to_list()
    
    day_total = Decimal("0")
    month_total = Decimal("0")
    paid_total = Decimal("0")
    paid_count = 0
    refund_pending = 0

    transactions = []

    for payment in all_payments:
        reservation = await Reservation.get(payment.reservation_id) if payment.reservation_id else None
        user = await User.get(reservation.user_id) if reservation and reservation.user_id else None
        
        amount = to_decimal(payment.amount)
        payment_status = normalize_status(payment.status)
        reservation_status = normalize_status(reservation.status) if reservation else ""
        is_paid = payment_status in ACCEPTED_PAYMENT_STATUS

        if is_paid:
            paid_total += amount
            paid_count += 1

            if payment.created_at and payment.created_at >= month_start:
                month_total += amount
            if payment.created_at and payment.created_at >= day_start:
                day_total += amount

        if reservation_status == "cancelled" and is_paid:
            refund_pending += 1

        transactions.append({
            "id": str(payment.id),
            "folio": f"VT-{str(payment.id)[-6:].upper()}",
            "client": user.full_name if user else "Sin cliente",
            "channel": reservation.pickup_location if reservation else "-",
            "payment_method": normalize_status(payment.method) or "efectivo",
            "amount": float(amount),
            "status": payment_status,
            "reservation_status": reservation_status or "pending",
            "refund_status": infer_refund_status(reservation_status, payment_status, is_paid),
            "is_paid": is_paid,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
        })

    closed_reservations = await Reservation.find(Reservation.status == ReservationStatus.COMPLETED).count()
    cancelled_reservations = await Reservation.find(Reservation.status == ReservationStatus.CANCELLED).count()

    average_ticket = (paid_total / paid_count) if paid_count else Decimal("0")

    return {
        "totals": {
            "day_total": float(day_total),
            "month_total": float(month_total),
            "closed_reservations": closed_reservations,
            "cancelled_reservations": cancelled_reservations,
            "refund_pending": refund_pending,
            "average_ticket": float(average_ticket),
        },
        "transactions": transactions[:limit],
    }


@router.get("/payment-alerts")
async def get_payment_alerts(
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_admin),
):
    """Obtener alertas de pagos pendientes"""
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(days=PAYMENT_ALERT_THRESHOLD_DAYS)

    reservations = await Reservation.find(
        {
            "status": "pending",
            "created_at": {"$lte": cutoff}
        }
    ).limit(limit).to_list()

    alerts = []
    for reservation in reservations:
        user = await User.get(reservation.user_id) if reservation.user_id else None
        vehicle = await Vehicle.get(reservation.vehicle_id) if reservation.vehicle_id else None
        
        days_overdue = (now_utc - reservation.created_at).days
        
        alerts.append({
            "id": str(reservation.id),
            "client": user.full_name if user else "Sin cliente",
            "vehicle": f"{vehicle.brand} {vehicle.model}" if vehicle else "Sin vehículo",
            "days_overdue": days_overdue,
            "amount": float(reservation.total_price or 0),
            "created_at": reservation.created_at.isoformat() if reservation.created_at else None,
        })

    return {"alerts": alerts}


@router.get("/crm")
async def get_crm_cases(
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(require_admin),
):
    """Obtener casos de CRM (tickets de soporte)"""
    now_utc = datetime.now(timezone.utc)
    sla_threshold = now_utc - timedelta(hours=CRM_SLA_HOURS)

    tickets = await SupportTicket.find_all().limit(limit).to_list()

    total_cases = len(tickets)
    open_cases = sum(1 for t in tickets if normalize_case_status(t.status) == "abierto")
    high_priority = sum(1 for t in tickets if t.priority == "high")
    
    # Contar reembolsos pendientes (simplificado)
    refund_pending = 0

    cases = []
    for ticket in tickets:
        user = await User.get(ticket.user_id) if ticket.user_id else None
        reservation = await Reservation.get(ticket.reservation_id) if ticket.reservation_id else None
        
        case_status = normalize_case_status(ticket.status)
        reservation_status = normalize_status(reservation.status) if reservation else "no_aplica"
        
        cases.append({
            "id": str(ticket.id),
            "folio": f"CRM-{str(ticket.id)[-6:].upper()}",
            "client": user.full_name if user else "Sin cliente",
            "contact": user.email if user else "-",
            "type": ticket.category or "general",
            "priority": ticket.priority or "medium",
            "status": case_status,
            "reservation_status": reservation_status,
            "refund_status": "no_aplica",
            "channel": "web",
            "amount": float(reservation.total_price) if reservation else 0,
            "is_invoice_required": False,
            "last_update": ticket.updated_at.isoformat() if ticket.updated_at else ticket.created_at.isoformat(),
            "message": ticket.message or "",
        })

    return {
        "totals": {
            "total_cases": total_cases,
            "open_cases": open_cases,
            "high_priority": high_priority,
            "refund_pending": refund_pending,
        },
        "cases": cases,
    }


@router.get("/users")
async def get_users(
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_admin),
):
    """Obtener lista de usuarios"""
    users = await User.find_all().limit(limit).to_list()
    
    return {
        "users": [
            {
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone or "-",
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in users
        ]
    }


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    update: AdminUserRoleUpdate,
    _: User = Depends(require_admin),
):
    """Actualizar rol de usuario"""
    try:
        object_id = PydanticObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")
    
    user = await User.get(object_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    normalized_role = normalize_role(update.role)
    user.role = UserRole(normalized_role)
    await user.save()
    
    return {"message": "Rol actualizado correctamente", "user_id": user_id, "new_role": normalized_role}


@router.get("/reservations")
async def get_reservations(
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_admin),
):
    """Obtener lista de reservaciones"""
    reservations = await Reservation.find_all().limit(limit).to_list()
    
    result = []
    for reservation in reservations:
        user = await User.get(reservation.user_id) if reservation.user_id else None
        vehicle = await Vehicle.get(reservation.vehicle_id) if reservation.vehicle_id else None
        
        result.append({
            "id": str(reservation.id),
            "client": user.full_name if user else "Sin cliente",
            "vehicle": f"{vehicle.brand} {vehicle.model}" if vehicle else "Sin vehículo",
            "start": reservation.start_date.isoformat() if reservation.start_date else None,
            "end": reservation.end_date.isoformat() if reservation.end_date else None,
            "status": reservation.status,
            "admin_notes": reservation.admin_notes or "",
            "created_at": reservation.created_at.isoformat() if reservation.created_at else None,
        })
    
    return {"reservations": result}


@router.patch("/reservations/{reservation_id}")
async def update_reservation(
    reservation_id: str,
    update: AdminReservationUpdate,
    _: User = Depends(require_admin),
):
    """Actualizar reservación"""
    try:
        object_id = PydanticObjectId(reservation_id)
    except:
        raise HTTPException(status_code=400, detail="ID de reservación inválido")
    
    reservation = await Reservation.get(object_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    if update.status is not None:
        normalized_status = normalize_status(update.status)
        if normalized_status not in ALLOWED_RESERVATION_STATUS:
            raise HTTPException(status_code=400, detail=f"Estado no válido: {update.status}")
        reservation.status = ReservationStatus(normalized_status)
    
    if update.admin_notes is not None:
        reservation.admin_notes = update.admin_notes[:1500]
    
    reservation.updated_at = datetime.now(timezone.utc)
    await reservation.save()
    
    return {"message": "Reservación actualizada correctamente", "reservation_id": reservation_id}


@router.get("/vehicles")
async def get_vehicles(
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_admin),
):
    """Obtener lista de vehículos"""
    vehicles = await Vehicle.find_all().limit(limit).to_list()
    
    return {
        "vehicles": [
            {
                "id": str(vehicle.id),
                "brand": vehicle.brand,
                "model": vehicle.model,
                "year": vehicle.year,
                "plate": vehicle.plate,
                "price_per_day": float(vehicle.price_per_day),
                "status": vehicle.status,
                "is_active": vehicle.is_active,
            }
            for vehicle in vehicles
        ]
    }


@router.patch("/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: str,
    update: AdminVehicleUpdate,
    _: User = Depends(require_admin),
):
    """Actualizar vehículo"""
    try:
        object_id = PydanticObjectId(vehicle_id)
    except:
        raise HTTPException(status_code=400, detail="ID de vehículo inválido")
    
    vehicle = await Vehicle.get(object_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    if update.status is not None:
        normalized_status = normalize_status(update.status)
        if normalized_status not in ALLOWED_VEHICLE_STATUS:
            raise HTTPException(status_code=400, detail=f"Estado no válido: {update.status}")
        vehicle.status = VehicleStatus(normalized_status)
    
    if update.is_active is not None:
        vehicle.is_active = update.is_active
    
    if update.price_per_day is not None:
        vehicle.price_per_day = float(update.price_per_day)
    
    if update.price_per_hour is not None:
        vehicle.price_per_hour = float(update.price_per_hour)
    
    vehicle.updated_at = datetime.now(timezone.utc)
    await vehicle.save()
    
    return {"message": "Vehículo actualizado correctamente", "vehicle_id": vehicle_id}
