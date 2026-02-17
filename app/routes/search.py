from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.db_models import Vehicle
from datetime import date, datetime
from typing import List, Optional

router = APIRouter()

# Ciudades principales de México
CIUDADES_MEXICO = [
    "Aguascalientes", "Campeche", "Cancún", "Celaya", "Chetumal", "Chihuahua",
    "Ciudad de México", "Ciudad Juárez", "Ciudad Victoria", "Colima", "Cuernavaca",
    "Culiacán", "Durango", "Ensenada", "Guadalajara", "Guanajuato", "Hermosillo",
    "Irapuato", "La Paz", "León", "Los Mochis", "Manzanillo", "Matamoros",
    "Mazatlán", "Mérida", "Mexicali", "Monterrey", "Morelia", "Nogales",
    "Nuevo Laredo", "Oaxaca", "Pachuca", "Playa del Carmen", "Puebla", "Puerto Vallarta",
    "Querétaro", "Reynosa", "Saltillo", "San Luis Potosí", "San Miguel de Allende",
    "Tampico", "Tapachula", "Tepic", "Tijuana", "Toluca", "Torreón", "Tuxtla Gutiérrez",
    "Uruapan", "Veracruz", "Villahermosa", "Zacatecas"
]


@router.get("/cities")
async def get_cities(q: Optional[str] = None):
    """Obtiene lista de ciudades de México, con filtro opcional"""
    if q:
        # Filtrar ciudades que contengan el query (case insensitive)
        filtered_cities = [city for city in CIUDADES_MEXICO if q.lower() in city.lower()]
        return {"cities": sorted(filtered_cities)}
    
    return {"cities": sorted(CIUDADES_MEXICO)}


@router.get("/vehicles")
async def search_vehicles(
    origin: Optional[str] = Query(None, description="Ciudad de origen"),
    destination: Optional[str] = Query(None, description="Ciudad de destino"),
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    capacity: Optional[int] = Query(None, description="Capacidad mínima de pasajeros"),
    vehicle_type: Optional[str] = Query(None, description="Tipo de vehículo"),
    db: Session = Depends(get_db)
):
    """Buscar vehículos disponibles con filtros"""
    
    # Query base - solo vehículos activos y disponibles
    query = db.query(Vehicle).filter(
        Vehicle.is_active == True,
        Vehicle.status == 'available'
    )
    
    # Aplicar filtros
    if capacity:
        query = query.filter(Vehicle.capacity >= capacity)
    
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type)
    
    vehicles = query.order_by(Vehicle.price_per_day.asc()).all()
    
    # Formatear respuesta
    results = []
    for vehicle in vehicles:
        results.append({
            "id": vehicle.id,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "vehicle_type": vehicle.vehicle_type,
            "capacity": vehicle.capacity,
            "plate": vehicle.plate,
            "color": vehicle.color,
            "price_per_day": float(vehicle.price_per_day),
            "price_per_hour": float(vehicle.price_per_hour) if vehicle.price_per_hour else None,
            "description": vehicle.description,
            "features": vehicle.features,
            "image_url": vehicle.image_url,
            "status": vehicle.status
        })
    
    return {
        "total": len(results),
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "vehicles": results
    }
