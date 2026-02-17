"""
Script para agregar vehículos de ejemplo a la base de datos
"""
from app.db import SessionLocal
from app.db_models import Vehicle
from decimal import Decimal

def seed_vehicles():
    """Agrega vehículos de ejemplo"""
    
    db = SessionLocal()
    
    try:
        # Verificar si ya hay vehículos
        existing = db.query(Vehicle).count()
        if existing > 0:
            print(f"ℹ️  Ya existen {existing} vehículos en la base de datos")
            return
        
        vehicles = [
            # Vans
            Vehicle(
                brand="Toyota",
                model="Hiace",
                year=2022,
                vehicle_type="van",
                capacity=12,
                plate="ABC-1234",
                color="Blanco",
                price_per_day=Decimal("150.00"),
                price_per_hour=Decimal("25.00"),
                description="Van espaciosa ideal para grupos grandes",
                features='{"ac": true, "gps": true, "bluetooth": true, "usb_ports": true}',
                image_url="https://images.unsplash.com/photo-1527786356703-4b100091cd2c?w=800",
                status="available",
                is_active=True
            ),
            Vehicle(
                brand="Mercedes-Benz",
                model="Sprinter",
                year=2023,
                vehicle_type="van",
                capacity=15,
                plate="XYZ-5678",
                color="Negro",
                price_per_day=Decimal("200.00"),
                price_per_hour=Decimal("35.00"),
                description="Van premium con máximo confort",
                features='{"ac": true, "gps": true, "bluetooth": true, "leather_seats": true, "wifi": true}',
                image_url="https://images.unsplash.com/photo-1619767886558-efdc259cde1a?w=800",
                status="available",
                is_active=True
            ),
            
            # Pickups
            Vehicle(
                brand="Ford",
                model="F-150",
                year=2023,
                vehicle_type="pickup",
                capacity=5,
                plate="DEF-9012",
                color="Azul",
                price_per_day=Decimal("120.00"),
                price_per_hour=Decimal("20.00"),
                description="Pickup robusta ideal para carga",
                features='{"ac": true, "4x4": true, "extended_bed": true}',
                image_url="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800",
                status="available",
                is_active=True
            ),
            Vehicle(
                brand="Chevrolet",
                model="Silverado",
                year=2022,
                vehicle_type="pickup",
                capacity=5,
                plate="GHI-3456",
                color="Rojo",
                price_per_day=Decimal("110.00"),
                price_per_hour=Decimal("18.00"),
                description="Pickup confiable para trabajo pesado",
                features='{"ac": true, "4x4": true, "trailer_hitch": true}',
                image_url="https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800",
                status="available",
                is_active=True
            ),
            
            # SUVs
            Vehicle(
                brand="Toyota",
                model="Land Cruiser",
                year=2023,
                vehicle_type="suv",
                capacity=7,
                plate="JKL-7890",
                color="Negro",
                price_per_day=Decimal("180.00"),
                price_per_hour=Decimal("30.00"),
                description="SUV de lujo para viajes familiares",
                features='{"ac": true, "4x4": true, "gps": true, "leather_seats": true, "sunroof": true}',
                image_url="https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800",
                status="available",
                is_active=True
            ),
            Vehicle(
                brand="Nissan",
                model="Pathfinder",
                year=2022,
                vehicle_type="suv",
                capacity=7,
                plate="MNO-2345",
                color="Gris",
                price_per_day=Decimal("140.00"),
                price_per_hour=Decimal("23.00"),
                description="SUV familiar cómodo y espacioso",
                features='{"ac": true, "gps": true, "bluetooth": true, "backup_camera": true}',
                image_url="https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=800",
                status="available",
                is_active=True
            ),
            
            # Camiones
            Vehicle(
                brand="Isuzu",
                model="NPR",
                year=2021,
                vehicle_type="truck",
                capacity=3,
                plate="PQR-6789",
                color="Blanco",
                price_per_day=Decimal("250.00"),
                description="Camión de carga mediana ideal para mudanzas",
                features='{"ac": true, "lift_gate": true, "cargo_capacity_3ton": true}',
                image_url="https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800",
                status="available",
                is_active=True
            ),
            Vehicle(
                brand="Hino",
                model="Serie 300",
                year=2022,
                vehicle_type="truck",
                capacity=3,
                plate="STU-0123",
                color="Blanco",
                price_per_day=Decimal("280.00"),
                description="Camión de carga para distribución",
                features='{"ac": true, "cargo_capacity_5ton": true, "hydraulic_lift": true}',
                image_url="https://images.unsplash.com/photo-1566847438217-76e82d383f84?w=800",
                status="available",
                is_active=True
            ),
            
            # Minibuses
            Vehicle(
                brand="Mercedes-Benz",
                model="Sprinter Passenger",
                year=2023,
                vehicle_type="minibus",
                capacity=20,
                plate="VWX-4567",
                color="Plateado",
                price_per_day=Decimal("300.00"),
                price_per_hour=Decimal("50.00"),
                description="Minibús de lujo para eventos y excursiones",
                features='{"ac": true, "gps": true, "bluetooth": true, "tv_screens": true, "wifi": true, "reclining_seats": true}',
                image_url="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800",
                status="available",
                is_active=True
            ),
            Vehicle(
                brand="Volkswagen",
                model="Crafter",
                year=2022,
                vehicle_type="minibus",
                capacity=18,
                plate="YZA-8901",
                color="Blanco",
                price_per_day=Decimal("270.00"),
                price_per_hour=Decimal("45.00"),
                description="Minibús cómodo para grupos medianos",
                features='{"ac": true, "gps": true, "bluetooth": true, "usb_charging": true}',
                image_url="https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=800",
                status="available",
                is_active=True
            ),
        ]
        
        # Agregar todos los vehículos
        for vehicle in vehicles:
            db.add(vehicle)
        
        db.commit()
        print(f"✅ Se agregaron {len(vehicles)} vehículos exitosamente")
        print("\nVehículos agregados:")
        for v in vehicles:
            print(f"  - {v.brand} {v.model} ({v.vehicle_type}) - ${v.price_per_day}/día")
        
    except Exception as e:
        print(f"❌ Error al agregar vehículos: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Agregando vehículos de ejemplo a la base de datos...\n")
    seed_vehicles()
