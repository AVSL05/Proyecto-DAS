from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import TransportSearchRequest, SearchResponse, TransportResult, TransportType
from datetime import date, datetime
from typing import List

router = APIRouter()

# Base de datos simulada (en producción usar PostgreSQL/MongoDB)
transports_db = [
    {
        "id": 1,
        "tipo": TransportType.BUS,
        "origen": "Ciudad de México",
        "destino": "Guadalajara",
        "fecha_salida": date(2026, 2, 10),
        "hora_salida": "08:00",
        "capacidad": 40,
        "precio": 450.00,
        "disponible": True,
        "empresa": "Cuidado con el pug"
    },
    {
        "id": 2,
        "tipo": TransportType.VAN,
        "origen": "Monterrey",
        "destino": "San Luis Potosí",
        "fecha_salida": date(2026, 2, 15),
        "hora_salida": "10:30",
        "capacidad": 15,
        "precio": 350.00,
        "disponible": True,
        "empresa": "Cuidado con el pug"
    },
    {
        "id": 3,
        "tipo": TransportType.AUTOBUS,
        "origen": "Cancún",
        "destino": "Playa del Carmen",
        "fecha_salida": date(2026, 2, 20),
        "hora_salida": "14:00",
        "capacidad": 50,
        "precio": 200.00,
        "disponible": True,
        "empresa": "Cuidado con el pug"
    }
]

@router.post("/transport", response_model=SearchResponse)
async def search_transport(search_request: TransportSearchRequest):
    """
    Endpoint para buscar transportes disponibles según criterios de búsqueda
    
    - **origen**: Ubicación de salida
    - **destino**: Ubicación de llegada
    - **fecha_salida**: Fecha del viaje
    - **num_pasajeros**: Cantidad de pasajeros
    """
    try:
        # Filtrar transportes según criterios
        resultados = []
        for transport in transports_db:
            if (transport["origen"].lower() == search_request.origen.lower() and
                transport["destino"].lower() == search_request.destino.lower() and
                transport["fecha_salida"] >= search_request.fecha_salida and
                transport["capacidad"] >= search_request.num_pasajeros and
                transport["disponible"]):
                resultados.append(TransportResult(**transport))
        
        return SearchResponse(
            resultados=resultados,
            total=len(resultados)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar transportes: {str(e)}")

@router.get("/locations")
async def get_locations():
    """
    Endpoint para obtener las ubicaciones disponibles
    """
    # Extraer ubicaciones únicas de la base de datos
    origenes = set(t["origen"] for t in transports_db)
    destinos = set(t["destino"] for t in transports_db)
    
    ubicaciones = list(origenes.union(destinos))
    
    return {
        "ubicaciones": sorted(ubicaciones),
        "total": len(ubicaciones)
    }

@router.get("/available-dates")
async def get_available_dates(
    origen: str = Query(..., description="Ubicación de origen"),
    destino: str = Query(..., description="Ubicación de destino")
):
    """
    Endpoint para obtener fechas disponibles para una ruta específica
    """
    fechas_disponibles = []
    
    for transport in transports_db:
        if (transport["origen"].lower() == origen.lower() and
            transport["destino"].lower() == destino.lower() and
            transport["disponible"]):
            fechas_disponibles.append(transport["fecha_salida"])
    
    return {
        "origen": origen,
        "destino": destino,
        "fechas_disponibles": sorted(set(fechas_disponibles)),
        "total": len(set(fechas_disponibles))
    }
