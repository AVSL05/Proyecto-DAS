from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Optional

from app.db import get_db
from app.db_models import Vehicle
from app.schemas_reservations import VehicleOut, VehicleListOut

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])


@router.get("/", response_model=VehicleListOut)
def list_vehicles(
    vehicle_type: Optional[str] = None,
    min_capacity: Optional[int] = None,
    max_price: Optional[float] = None,
    is_available: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listar vehículos disponibles con filtros"""
    
    query = db.query(Vehicle)
    
    # Filtrar por activos
    if is_available:
        query = query.filter(Vehicle.is_active == True, Vehicle.status == 'available')
    
    # Filtros opcionales
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type)
    
    if min_capacity:
        query = query.filter(Vehicle.capacity >= min_capacity)
    
    if max_price:
        query = query.filter(Vehicle.price_per_day <= max_price)
    
    total = query.count()
    vehicles = query.order_by(Vehicle.price_per_day.asc()).offset(skip).limit(limit).all()
    
    return VehicleListOut(vehicles=vehicles, total=total)


@router.get("/types")
def get_vehicle_types(db: Session = Depends(get_db)):
    """Obtener tipos de vehículos disponibles"""
    types = db.query(Vehicle.vehicle_type).filter(Vehicle.is_active == True).distinct().all()
    return {"vehicle_types": [t[0] for t in types]}


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Obtener detalles de un vehículo específico"""
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    return vehicle


@router.get("/{vehicle_id}/availability")
def check_vehicle_availability(
    vehicle_id: int,
    start_date: datetime = Query(..., description="Fecha de inicio (ISO format)"),
    end_date: datetime = Query(..., description="Fecha de fin (ISO format)"),
    db: Session = Depends(get_db)
):
    """Verificar disponibilidad de un vehículo en fechas específicas"""
    
    from app.routes.reservations import check_vehicle_availability as check_availability
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    is_available = check_availability(vehicle_id, start_date, end_date, db)
    
    return {
        "vehicle_id": vehicle_id,
        "start_date": start_date,
        "end_date": end_date,
        "is_available": is_available
    }
