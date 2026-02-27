from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.db_models import Invoice, Payment, Reservation, SupportTicket, User, UserRole, Vehicle
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
    price_per_day: Optional[Decimal] = Field(default=None, ge=0)
    price_per_hour: Optional[Decimal] = Field(default=None, ge=0)


class AdminUserRoleUpdate(BaseModel):
    role: str


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


def build_payment_alert_query(db: Session, cutoff: datetime):
    return (
        db.query(Reservation)
        .options(joinedload(Reservation.user), joinedload(Reservation.payment))
        .filter(
            Reservation.status.in_(PAYMENT_ALERT_RESERVATION_STATUS),
            Reservation.created_at <= cutoff,
            ~Reservation.payment.has(Payment.status.in_(ACCEPTED_PAYMENT_STATUS)),
        )
    )


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
    now_utc = datetime.now(timezone.utc)
    alert_cutoff = now_utc - timedelta(days=PAYMENT_ALERT_THRESHOLD_DAYS)

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
    payment_alerts_count = build_payment_alert_query(db, alert_cutoff).count()

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
def get_admin_sales(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    now_utc = datetime.now(timezone.utc)
    day_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = day_start.replace(day=1)

    all_payments = (
        db.query(Payment)
        .options(
            joinedload(Payment.reservation).joinedload(Reservation.user),
        )
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
    refund_pending = 0

    for payment in all_payments:
        amount = to_decimal(payment.amount)
        created_at = to_utc_datetime(payment.created_at)
        payment_status = normalize_status(payment.status)
        reservation = payment.reservation
        reservation_status = normalize_status(reservation.status if reservation else "")
        is_paid = payment_status in ACCEPTED_PAYMENT_STATUS

        if is_paid:
            paid_total += amount
            paid_count += 1

            if created_at and created_at >= month_start:
                month_total += amount
            if created_at and created_at >= day_start:
                day_total += amount

        if reservation_status == "cancelled" and is_paid:
            refund_pending += 1

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
    cancelled_reservations = (
        db.query(Reservation)
        .filter(Reservation.status == "cancelled")
        .count()
    )

    average_ticket = (paid_total / paid_count) if paid_count else Decimal("0")

    transactions = []

    for payment in all_payments:
        reservation = payment.reservation
        if not reservation:
            continue

        payment_status = normalize_status(payment.status) or "accepted"
        reservation_status = normalize_status(reservation.status)
        is_paid = payment_status in ACCEPTED_PAYMENT_STATUS or (
            not payment and reservation_status in PAID_RESERVATION_STATUS
        )
        refund_status = infer_refund_status(reservation_status, payment_status, is_paid)

        transactions.append(
            {
                "id": reservation.id,
                "folio": f"VT-{reservation.id:04d}",
                "client": reservation.user.full_name if reservation.user else "Sin cliente",
                "channel": reservation.pickup_location or "-",
                "payment_method": normalize_status(payment.method) or "efectivo",
                "amount": float(to_decimal(payment.amount)),
                "status": payment_status,
                "reservation_status": reservation_status or "pending",
                "refund_status": refund_status,
                "is_paid": is_paid,
                "created_at": payment.created_at,
            }
        )

    for reservation in legacy_paid_reservations:
        status_value = normalize_status(reservation.status)
        transactions.append(
            {
                "id": reservation.id,
                "folio": f"VT-{reservation.id:04d}",
                "client": reservation.user.full_name if reservation.user else "Sin cliente",
                "channel": reservation.pickup_location or "-",
                "payment_method": "sin_registro",
                "amount": float(to_decimal(reservation.total_price)),
                "status": status_value,
                "reservation_status": status_value,
                "refund_status": infer_refund_status(
                    status_value,
                    "",
                    status_value in PAID_RESERVATION_STATUS,
                ),
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
            "cancelled_reservations": cancelled_reservations,
            "average_ticket": float(average_ticket),
            "paid_count": paid_count,
            "refund_pending": refund_pending,
        },
        "transactions": transactions,
    }


@router.get("/payment-alerts")
def get_payment_alerts(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(days=PAYMENT_ALERT_THRESHOLD_DAYS)

    query = build_payment_alert_query(db, cutoff)
    total = query.count()
    reservations = query.order_by(Reservation.created_at.asc()).limit(limit).all()

    alerts = []
    for reservation in reservations:
        created_at = to_utc_datetime(reservation.created_at)
        days_without_payment = 0
        if created_at:
            days_without_payment = max(0, (now_utc - created_at).days)

        alerts.append(
            {
                "reservation_id": reservation.id,
                "folio": f"VT-{reservation.id:04d}",
                "client": reservation.user.full_name if reservation.user else "Sin cliente",
                "email": reservation.user.email if reservation.user else None,
                "status": normalize_status(reservation.status) or "pending",
                "amount_due": float(to_decimal(reservation.total_price)),
                "days_without_payment": days_without_payment,
                "created_at": reservation.created_at,
            }
        )

    return {
        "total": total,
        "threshold_days": PAYMENT_ALERT_THRESHOLD_DAYS,
        "alerts": alerts,
    }


@router.get("/crm")
def get_crm_cases(
    limit: int = Query(default=80, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    now_utc = datetime.now(timezone.utc)
    payment_alert_cutoff = now_utc - timedelta(days=PAYMENT_ALERT_THRESHOLD_DAYS)

    tickets = (
        db.query(SupportTicket)
        .options(
            joinedload(SupportTicket.reservation).joinedload(Reservation.user),
            joinedload(SupportTicket.reservation).joinedload(Reservation.payment),
            joinedload(SupportTicket.reservation).joinedload(Reservation.invoice),
        )
        .order_by(SupportTicket.created_at.desc())
        .limit(limit * 2)
        .all()
    )

    reservations = (
        db.query(Reservation)
        .options(
            joinedload(Reservation.user),
            joinedload(Reservation.payment),
            joinedload(Reservation.invoice),
        )
        .order_by(Reservation.created_at.desc())
        .limit(limit * 2)
        .all()
    )

    cases = []
    ticketed_reservation_ids = set()

    for ticket in tickets:
        reservation = ticket.reservation
        if not reservation:
            continue

        ticketed_reservation_ids.add(reservation.id)

        reservation_status = normalize_status(reservation.status)
        payment = reservation.payment
        payment_status = normalize_status(payment.status if payment else "")
        is_paid = payment_status in ACCEPTED_PAYMENT_STATUS or reservation_status in PAID_RESERVATION_STATUS
        updated_at = to_utc_datetime(ticket.updated_at) or to_utc_datetime(ticket.created_at)
        refund_status = infer_refund_status(reservation_status, payment_status, is_paid)
        case_status = normalize_case_status(ticket.status)
        issue_type = normalize_status(ticket.issue_type) or "general"

        priority = "media"
        if issue_type in {"reembolso", "refund", "cancelacion", "cancelación"}:
            priority = "alta"
        if refund_status == "pendiente":
            priority = "alta"

        sla_at_risk = False
        if case_status == "abierto" and updated_at:
            sla_at_risk = (now_utc - updated_at) >= timedelta(hours=CRM_SLA_HOURS)

        invoice = reservation.invoice
        invoice_number = invoice.invoice_number if invoice else None

        cases.append(
            {
                "case_id": f"TCK-{ticket.id:05d}",
                "ticket_id": ticket.id,
                "source": "ticket",
                "reservation_id": reservation.id,
                "folio": ticket.folio or f"VT-{reservation.id:04d}",
                "client": reservation.user.full_name if reservation.user else "Sin cliente",
                "email": ticket.contact_email or (reservation.user.email if reservation.user else None),
                "phone": ticket.contact_phone or (reservation.user.phone if reservation.user else None),
                "case_type": f"Ticket cliente: {issue_type}",
                "priority": priority,
                "status": case_status,
                "reservation_status": reservation_status or "pending",
                "refund_status": refund_status,
                "channel": reservation.pickup_location or "-",
                "amount": float(to_decimal(reservation.total_price)),
                "invoice_number": invoice_number,
                "message": ticket.message,
                "last_update": updated_at,
                "sla_at_risk": sla_at_risk,
            }
        )

        if len(cases) >= limit:
            break

    for reservation in reservations:
        if reservation.id in ticketed_reservation_ids:
            continue

        reservation_status = normalize_status(reservation.status)
        payment = reservation.payment
        payment_status = normalize_status(payment.status if payment else "")
        is_paid = payment_status in ACCEPTED_PAYMENT_STATUS or (
            not payment and reservation_status in PAID_RESERVATION_STATUS
        )
        created_at = to_utc_datetime(reservation.created_at)
        updated_at = to_utc_datetime(reservation.updated_at) or created_at

        case_type = None
        priority = "media"
        case_status = "abierto"
        refund_status = infer_refund_status(reservation_status, payment_status, is_paid)

        if reservation_status == "cancelled":
            case_type = "Cancelacion o reembolso"
            priority = "alta" if refund_status == "pendiente" else "media"
            case_status = "abierto" if refund_status == "pendiente" else "cerrado"
        elif created_at and created_at <= payment_alert_cutoff and not is_paid:
            case_type = "Pago vencido"
            priority = "alta"
        elif reservation_status in ACTIVE_RESERVATION_STATUS:
            case_type = "Seguimiento de reserva"
            priority = "media"

        if not case_type:
            continue

        sla_at_risk = False
        if case_status == "abierto" and updated_at:
            sla_at_risk = (now_utc - updated_at) >= timedelta(hours=CRM_SLA_HOURS)

        invoice = reservation.invoice
        invoice_number = invoice.invoice_number if invoice else None

        cases.append(
            {
                "case_id": f"OPS-{reservation.id:05d}",
                "ticket_id": None,
                "source": "operacion",
                "reservation_id": reservation.id,
                "folio": f"VT-{reservation.id:04d}",
                "client": reservation.user.full_name if reservation.user else "Sin cliente",
                "email": reservation.user.email if reservation.user else None,
                "phone": reservation.user.phone if reservation.user else None,
                "case_type": case_type,
                "priority": priority,
                "status": case_status,
                "reservation_status": reservation_status or "pending",
                "refund_status": refund_status,
                "channel": reservation.pickup_location or "-",
                "amount": float(to_decimal(reservation.total_price)),
                "invoice_number": invoice_number,
                "message": reservation.admin_notes or reservation.notes or "Sin notas adicionales.",
                "last_update": updated_at,
                "sla_at_risk": sla_at_risk,
            }
        )

        if len(cases) >= limit:
            break

    cases = sorted(
        cases,
        key=lambda case: to_utc_datetime(case.get("last_update")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )[:limit]

    open_cases = [case for case in cases if normalize_case_status(case["status"]) == "abierto"]
    high_priority = [case for case in open_cases if case["priority"] == "alta"]
    refunds_pending = [case for case in open_cases if case["refund_status"] == "pendiente"]
    sla_at_risk = [case for case in open_cases if case["sla_at_risk"]]

    return {
        "totals": {
            "total_cases": len(cases),
            "open_cases": len(open_cases),
            "high_priority": len(high_priority),
            "refund_pending": len(refunds_pending),
            "sla_at_risk": len(sla_at_risk),
        },
        "cases": cases,
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

        if status_value in {"confirmed", "in_progress"} and reservation.vehicle_id:
            vehicle = db.query(Vehicle).filter(Vehicle.id == reservation.vehicle_id).first()
            if vehicle:
                vehicle.status = "reserved"

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
