from fastapi import APIRouter, Query
from app.mongodb_models import Vehicle
from typing import Optional

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
    vehicle_type: Optional[str] = Query(None, description="Tipo de vehículo")
):
    """Buscar vehículos disponibles con filtros en MongoDB"""
    
    # Query base - solo vehículos activos y disponibles
    filters = {
        "is_active": True,
        "status": "available"
    }
    
    # Aplicar filtros
    if capacity:
        filters["capacity"] = {"$gte": capacity}
    
    if vehicle_type:
        filters["vehicle_type"] = vehicle_type
    
    vehicles = await Vehicle.find(filters).sort("+price_per_day").to_list()
    
    # Formatear respuesta
    results = []
    for vehicle in vehicles:
        results.append({
            "id": str(vehicle.id),  # MongoDB usa string IDs
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
