#!/usr/bin/env python3
"""
Script para probar la funcionalidad de búsqueda
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_cities():
    """Prueba el endpoint de ciudades"""
    print("\n=== Test: Obtener ciudades de México ===")
    response = requests.get(f"{BASE_URL}/search/cities")
    data = response.json()
    print(f"✅ Total de ciudades: {len(data['cities'])}")
    print(f"Primeras 5: {data['cities'][:5]}")
    
    # Filtrar ciudades
    print("\n=== Test: Filtrar ciudades con 'Guad' ===")
    response = requests.get(f"{BASE_URL}/search/cities?q=Guad")
    data = response.json()
    print(f"✅ Ciudades encontradas: {data['cities']}")

def test_vehicle_search():
    """Prueba la búsqueda de vehículos"""
    print("\n=== Test: Buscar vehículos disponibles ===")
    
    params = {
        "origin": "Ciudad de México",
        "destination": "Guadalajara",
        "start_date": "2024-06-15",
        "capacity": 4
    }
    
    response = requests.get(f"{BASE_URL}/search/vehicles", params=params)
    data = response.json()
    
    print(f"✅ Vehículos encontrados: {data['total']}")
    
    if data['total'] > 0:
        print("\nPrimer vehículo:")
        vehicle = data['vehicles'][0]
        print(f"  - {vehicle['brand']} {vehicle['model']} ({vehicle['year']})")
        print(f"  - Tipo: {vehicle['vehicle_type']}")
        print(f"  - Capacidad: {vehicle['capacity']} pasajeros")
        print(f"  - Precio: ${vehicle['price_per_day']}/día")
        print(f"  - Estado: {vehicle['status']}")

def test_filters():
    """Prueba los filtros de búsqueda"""
    print("\n=== Test: Filtros avanzados ===")
    
    # Solo vans
    params = {
        "origin": "Ciudad de México",
        "destination": "Monterrey",
        "start_date": "2024-07-01",
        "capacity": 6,
        "vehicle_type": "van"
    }
    
    response = requests.get(f"{BASE_URL}/search/vehicles", params=params)
    data = response.json()
    
    print(f"✅ Vans con capacidad ≥6: {data['total']}")
    
    for vehicle in data['vehicles']:
        print(f"  - {vehicle['brand']} {vehicle['model']} - {vehicle['capacity']} pasajeros")

if __name__ == "__main__":
    try:
        print("🚀 Probando la funcionalidad de búsqueda...")
        test_cities()
        test_vehicle_search()
        test_filters()
        print("\n✅ ¡Todas las pruebas pasaron correctamente!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
