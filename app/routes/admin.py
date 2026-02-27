from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.db_models import Payment, Reservation, User, UserRole, Vehicle
from app.security import decode_access_token

router = APIRouter(prefix="/api/admin", tags=["Admin"])

ALLOWED_RESERVATION_STATUS = {"pending", "confirmed", "in_progress", "completed", "cancelled"}
ALLOWED_VEHICLE_STATUS = {"available", "reserved", "in_use", "maintenance", "unavailable"}
VALID_ROLES = {UserRole.CLIENT.value, UserRole.ADMIN.value}
PAID_RESERVATION_STATUS = {"confirmed", "in_progress", "completed"}
ACCEPTED_PAYMENT_STATUS = {"accepted"}


class AdminReservationUpdate(BaseModel):
    status: Optional[str] = Field(default=None)
    admin_notes: Optional[str] = Field(default=None, max_length=1500)


class AdminVehicleUpdate(BaseModel):
    status: Optional[str] = None
    is_active: Optional[bool] = None
    price_per_day: Optional[Decimal] = Field(default=None, ge=0)
    price_per_hour: Optional[Decimal] = Field(default=None, ge=0)


class AdminUserRoleUpdate(BaseModel):
    role: str


def normalize_role(role: Optional[str]) -> str:
    role_value = (role or UserRole.CLIENT.value).strip().lower()
    if role_value not in VALID_ROLES:
        return UserRole.CLIENT.value
    return role_value


def get_current_user_from_token(request: Request, db: Session) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticacion requerido")

    token = auth.split(" ", 1)[1].strip()

    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")

    email = (payload.get("sub") or "").lower().strip()
    if not email:
        raise HTTPException(status_code=401, detail="Token invalido")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user


def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    current_user = get_current_user_from_token(request, db)
    if normalize_role(current_user.role) != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acceso solo para rol administrativo")
    return current_user


@router.get("/summary")
def get_admin_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.role == UserRole.ADMIN.value).count()
    total_clients = total_users - total_admins

    total_reservations = db.query(Reservation).count()
    pending_reservations = db.query(Reservation).filter(Reservation.status == "pending").count()
    active_reservations = db.query(Reservation).filter(
        Reservation.status.in_(["pending", "confirmed", "in_progress"])
    ).count()

    total_vehicles = db.query(Vehicle).count()
    active_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).count()

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
    }


@router.get("/sales")
def get_admin_sales(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    now_utc = datetime.now(timezone.utc)
    day_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = day_start.replace(day=1)

    def to_decimal(value) -> Decimal:
        if value is None:
            return Decimal("0")
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def to_utc_datetime(value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    accepted_payments = (
        db.query(Payment)
        .options(
            joinedload(Payment.reservation).joinedload(Reservation.user),
        )
        .filter(Payment.status.in_(ACCEPTED_PAYMENT_STATUS))
        .all()
    )

    # Fallback para reservaciones antiguas sin registro en payments.
    legacy_paid_reservations = (
        db.query(Reservation)
        .options(joinedload(Reservation.user))
        .filter(
            Reservation.status.in_(PAID_RESERVATION_STATUS),
            ~Reservation.payment.has(),
        )
        .all()
    )

    day_total = Decimal("0")
    month_total = Decimal("0")
    paid_total = Decimal("0")
    paid_count = 0

    for payment in accepted_payments:
        amount = to_decimal(payment.amount)
        created_at = to_utc_datetime(payment.created_at)

        paid_total += amount
        paid_count += 1

        if created_at and created_at >= month_start:
            month_total += amount
        if created_at and created_at >= day_start:
            day_total += amount

    for reservation in legacy_paid_reservations:
        amount = to_decimal(reservation.total_price)
        created_at = to_utc_datetime(reservation.created_at)

        paid_total += amount
        paid_count += 1

        if created_at and created_at >= month_start:
            month_total += amount
        if created_at and created_at >= day_start:
            day_total += amount

    closed_reservations = (
        db.query(Reservation)
        .filter(Reservation.status == "completed")
        .count()
    )

    average_ticket = (paid_total / paid_count) if paid_count else Decimal("0")

    transactions = []

    for payment in accepted_payments:
        reservation = payment.reservation
        if not reservation:
            continue
        transactions.append(
            {
                "id": reservation.id,
                "folio": f"VT-{reservation.id:04d}",
                "client": reservation.user.full_name if reservation.user else "Sin cliente",
                "channel": reservation.pickup_location or "-",
                "amount": float(to_decimal(payment.amount)),
                "status": (payment.status or "").strip().lower() or "accepted",
                "is_paid": True,
                "created_at": payment.created_at,
            }
        )

    for reservation in legacy_paid_reservations:
        status_value = (reservation.status or "").strip().lower()
        transactions.append(
            {
                "id": reservation.id,
                "folio": f"VT-{reservation.id:04d}",
                "client": reservation.user.full_name if reservation.user else "Sin cliente",
                "channel": reservation.pickup_location or "-",
                "amount": float(to_decimal(reservation.total_price)),
                "status": status_value,
                "is_paid": status_value in PAID_RESERVATION_STATUS,
                "created_at": reservation.created_at,
            }
        )

    transactions.sort(
        key=lambda item: to_utc_datetime(item.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    transactions = transactions[:limit]

    return {
        "totals": {
            "day": float(day_total),
            "month": float(month_total),
            "closed_reservations": closed_reservations,
            "average_ticket": float(average_ticket),
            "paid_count": paid_count,
        },
        "transactions": transactions,
    }


@router.get("/users")
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(User).count()

    return {
        "total": total,
        "users": [
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "role": normalize_role(user.role),
                "created_at": user.created_at,
            }
            for user in users
        ],
    }


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: AdminUserRoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    role = (payload.role or "").strip().lower()
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Rol invalido")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.id == admin_user.id and role != UserRole.ADMIN.value:
        raise HTTPException(status_code=400, detail="No puedes quitarte tu propio rol administrativo")

    user.role = role
    db.commit()
    db.refresh(user)

    return {"message": "Rol actualizado", "user_id": user.id, "role": role}


@router.get("/reservations")
def list_reservations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(Reservation).options(
        joinedload(Reservation.user),
        joinedload(Reservation.vehicle),
    )
    total = query.count()
    reservations = query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "reservations": [
            {
                "id": reservation.id,
                "user_id": reservation.user_id,
                "user_name": reservation.user.full_name if reservation.user else None,
                "user_email": reservation.user.email if reservation.user else None,
                "vehicle_id": reservation.vehicle_id,
                "vehicle_name": (
                    f"{reservation.vehicle.brand} {reservation.vehicle.model}"
                    if reservation.vehicle
                    else None
                ),
                "start_date": reservation.start_date,
                "end_date": reservation.end_date,
                "pickup_location": reservation.pickup_location,
                "return_location": reservation.return_location,
                "status": reservation.status,
                "total_price": reservation.total_price,
                "admin_notes": reservation.admin_notes,
                "created_at": reservation.created_at,
            }
            for reservation in reservations
        ],
    }


@router.patch("/reservations/{reservation_id}")
def update_reservation(
    reservation_id: int,
    payload: AdminReservationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservacion no encontrada")

    if payload.status is not None:
        status_value = payload.status.strip().lower()
        if status_value not in ALLOWED_RESERVATION_STATUS:
            raise HTTPException(status_code=400, detail="Estatus de reservacion invalido")
        reservation.status = status_value

    if payload.admin_notes is not None:
        reservation.admin_notes = payload.admin_notes.strip()

    reservation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(reservation)

    return {
        "message": "Reservacion actualizada",
        "reservation_id": reservation.id,
        "status": reservation.status,
        "admin_notes": reservation.admin_notes,
    }


@router.get("/vehicles")
def list_vehicles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(Vehicle)
    total = query.count()
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "vehicles": [
            {
                "id": vehicle.id,
                "brand": vehicle.brand,
                "model": vehicle.model,
                "year": vehicle.year,
                "plate": vehicle.plate,
                "status": vehicle.status,
                "is_active": vehicle.is_active,
                "capacity": vehicle.capacity,
                "price_per_day": vehicle.price_per_day,
                "price_per_hour": vehicle.price_per_hour,
                "created_at": vehicle.created_at,
            }
            for vehicle in vehicles
        ],
    }


@router.patch("/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    payload: AdminVehicleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

    if payload.status is not None:
        status_value = payload.status.strip().lower()
        if status_value not in ALLOWED_VEHICLE_STATUS:
            raise HTTPException(status_code=400, detail="Estatus de vehiculo invalido")
        vehicle.status = status_value

    if payload.is_active is not None:
        vehicle.is_active = payload.is_active

    if payload.price_per_day is not None:
        vehicle.price_per_day = payload.price_per_day

    if payload.price_per_hour is not None:
        vehicle.price_per_hour = payload.price_per_hour

    vehicle.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(vehicle)

    return {
        "message": "Vehiculo actualizado",
        "vehicle_id": vehicle.id,
        "status": vehicle.status,
        "is_active": vehicle.is_active,
    }
