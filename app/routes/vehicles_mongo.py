from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional
from beanie import PydanticObjectId

from app.mongodb_models import Vehicle
from app.schemas_reservations_mongo import VehicleOut, VehicleListOut

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])


@router.get("/", response_model=VehicleListOut)
async def list_vehicles(
    vehicle_type: Optional[str] = None,
    min_capacity: Optional[int] = None,
    max_price: Optional[float] = None,
    is_available: bool = True,
    skip: int = 0,
    limit: int = 100,
):
    """Listar vehículos disponibles con filtros"""
    
    # Construir filtros dinámicos
    filters = {}
    
    # Filtrar por activos y disponibles
    if is_available:
        filters["is_active"] = True
        filters["status"] = "available"
    
    # Filtros opcionales
    if vehicle_type:
        filters["vehicle_type"] = vehicle_type
    
    if min_capacity:
        filters["capacity"] = {"$gte": min_capacity}
    
    if max_price:
        filters["price_per_day"] = {"$lte": max_price}
    
    # Contar total
    total = await Vehicle.find(filters).count()
    
    # Obtener vehículos con paginación
    vehicles = await Vehicle.find(filters).sort("+price_per_day").skip(skip).limit(limit).to_list()
    
    # Convertir a VehicleOut con id como string
    vehicles_out = []
    for v in vehicles:
        vehicle_dict = v.dict()
        vehicle_dict["id"] = str(v.id)
        vehicles_out.append(VehicleOut(**vehicle_dict))
    
    return VehicleListOut(vehicles=vehicles_out, total=total)


@router.get("/types")
async def get_vehicle_types():
    """Obtener tipos de vehículos disponibles"""
    # Usar agregación para obtener tipos únicos
    types = await Vehicle.find({"is_active": True}).distinct("vehicle_type")
    return {"vehicle_types": types}


@router.get("/{vehicle_id}", response_model=VehicleOut)
async def get_vehicle(vehicle_id: str):
    """Obtener detalles de un vehículo específico"""
    
    try:
        vehicle = await Vehicle.get(PydanticObjectId(vehicle_id))
    except Exception:
        raise HTTPException(status_code=400, detail="ID de vehículo inválido")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    vehicle_dict = vehicle.dict()
    vehicle_dict["id"] = str(vehicle.id)
    return VehicleOut(**vehicle_dict)


@router.get("/{vehicle_id}/availability")
async def check_vehicle_availability_endpoint(
    vehicle_id: str,
    start_date: datetime = Query(..., description="Fecha de inicio (ISO format)"),
    end_date: datetime = Query(..., description="Fecha de fin (ISO format)"),
):
    """Verificar disponibilidad de un vehículo en fechas específicas"""
    
    from app.routes.reservations_mongo import check_vehicle_availability
    
    try:
        vehicle = await Vehicle.get(PydanticObjectId(vehicle_id))
    except Exception:
        raise HTTPException(status_code=400, detail="ID de vehículo inválido")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    is_available = await check_vehicle_availability(vehicle_id, start_date, end_date)
    
    return {
        "vehicle_id": vehicle_id,
        "start_date": start_date,
        "end_date": end_date,
        "is_available": is_available
    }
