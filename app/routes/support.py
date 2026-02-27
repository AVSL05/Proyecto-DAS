import re
from datetime import datetime, timezone
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.db_models import Invoice, Reservation, SupportTicket

router = APIRouter(prefix="/api/support", tags=["Support"])

FOLIO_REGEX = re.compile(r"^VT-(\d{1,10})$")


class SupportTicketCreate(BaseModel):
    folio: str = Field(..., min_length=1, max_length=30)
    issue_type: str = Field(default="general", min_length=3, max_length=80)
    message: str = Field(..., min_length=8, max_length=1500)
    contact_name: Optional[str] = Field(default=None, max_length=120)
    contact_email: Optional[str] = Field(default=None, max_length=120)
    contact_phone: Optional[str] = Field(default=None, max_length=30)


def parse_folio(raw_folio: str) -> Tuple[int, str]:
    value = (raw_folio or "").strip().upper()
    if not value:
        raise HTTPException(status_code=400, detail="Folio requerido")

    if value.isdigit():
        reservation_id = int(value)
        return reservation_id, f"VT-{reservation_id:04d}"

    match = FOLIO_REGEX.match(value)
    if not match:
        raise HTTPException(status_code=400, detail="Formato de folio invalido. Usa VT-0001")

    reservation_id = int(match.group(1))
    return reservation_id, f"VT-{reservation_id:04d}"


def build_invoice_number(reservation_id: int, issued_at: datetime) -> str:
    return f"FAC-{issued_at.strftime('%Y%m%d')}-{reservation_id:06d}"


@router.post("/tickets")
def create_support_ticket(
    payload: SupportTicketCreate,
    db: Session = Depends(get_db),
):
    reservation_id, normalized_folio = parse_folio(payload.folio)

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="No se encontro la reservacion para ese folio")

    issue_type = payload.issue_type.strip().lower()
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Describe el problema del ticket")

    ticket = SupportTicket(
        reservation_id=reservation.id,
        folio=normalized_folio,
        issue_type=issue_type,
        message=message,
        contact_name=(payload.contact_name or "").strip() or None,
        contact_email=(payload.contact_email or "").strip() or None,
        contact_phone=(payload.contact_phone or "").strip() or None,
        status="open",
    )
    db.add(ticket)

    invoice = db.query(Invoice).filter(Invoice.reservation_id == reservation.id).first()
    if not invoice:
        issued_at = datetime.now(timezone.utc)
        invoice = Invoice(
            reservation_id=reservation.id,
            folio=normalized_folio,
            invoice_number=build_invoice_number(reservation.id, issued_at),
            amount=reservation.total_price,
            currency="MXN",
            status="generated",
            issued_at=issued_at,
        )
        db.add(invoice)

    db.commit()
    db.refresh(ticket)
    db.refresh(invoice)

    return {
        "message": "Ticket creado exitosamente",
        "ticket_id": ticket.id,
        "folio": ticket.folio,
        "reservation_id": reservation.id,
        "status": "abierto",
        "invoice_number": invoice.invoice_number,
        "invoice_folio": invoice.folio,
        "created_at": ticket.created_at,
    }
