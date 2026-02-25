"""
Script para migrar datos de SQLite a MongoDB
Ejecutar: python migrate_to_mongodb.py
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db_models import User as SQLUser, Vehicle as SQLVehicle, Reservation as SQLReservation
from app.db_models import PasswordResetToken as SQLPasswordResetToken

# MongoDB imports
from motor.motor_asyncio import AsyncIOMotorClient
from app.mongodb_models import (
    User, Vehicle, Reservation, PasswordResetToken,
    UserRole, VehicleStatus, ReservationStatus
)
from beanie import init_beanie
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
DATABASE_URL = "sqlite:///./dev.db"
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "proyecto_das_db")


async def migrate_users(db_session, mongodb_client):
    """Migrar usuarios de SQLite a MongoDB"""
    print("\n🔄 Migrando usuarios...")
    
    users = db_session.query(SQLUser).all()
    migrated = 0
    
    for sql_user in users:
        # Verificar si ya existe
        existing = await User.find_one(User.email == sql_user.email)
        if existing:
            print(f"  ⏭️  Usuario {sql_user.email} ya existe, omitiendo...")
            continue
        
        # Crear usuario MongoDB
        mongo_user = User(
            full_name=sql_user.full_name,
            email=sql_user.email,
            phone=sql_user.phone,
            password_hash=sql_user.password_hash,
            google_id=sql_user.google_id,
            avatar_url=sql_user.avatar_url,
            role=UserRole.ADMIN if sql_user.role == "administrativo" else UserRole.CLIENT,
            created_at=sql_user.created_at
        )
        
        await mongo_user.insert()
        migrated += 1
        print(f"  ✅ Migrado: {sql_user.email}")
    
    print(f"\n✨ {migrated} usuarios migrados de {len(users)} totales")
    return migrated


async def migrate_vehicles(db_session, mongodb_client):
    """Migrar vehículos de SQLite a MongoDB"""
    print("\n🔄 Migrando vehículos...")
    
    vehicles = db_session.query(SQLVehicle).all()
    migrated = 0
    
    for sql_vehicle in vehicles:
        # Verificar si ya existe
        existing = await Vehicle.find_one(Vehicle.plate == sql_vehicle.plate)
        if existing:
            print(f"  ⏭️  Vehículo {sql_vehicle.plate} ya existe, omitiendo...")
            continue
        
        # Crear vehículo MongoDB
        mongo_vehicle = Vehicle(
            brand=sql_vehicle.brand,
            model=sql_vehicle.model,
            year=sql_vehicle.year,
            vehicle_type=sql_vehicle.vehicle_type,
            capacity=sql_vehicle.capacity,
            plate=sql_vehicle.plate,
            color=sql_vehicle.color,
            price_per_day=float(sql_vehicle.price_per_day),
            price_per_hour=float(sql_vehicle.price_per_hour) if sql_vehicle.price_per_hour else None,
            description=sql_vehicle.description,
            features=sql_vehicle.features,
            image_url=sql_vehicle.image_url,
            status=VehicleStatus(sql_vehicle.status),
            is_active=sql_vehicle.is_active,
            created_at=sql_vehicle.created_at,
            updated_at=sql_vehicle.updated_at
        )
        
        await mongo_vehicle.insert()
        migrated += 1
        print(f"  ✅ Migrado: {sql_vehicle.brand} {sql_vehicle.model} ({sql_vehicle.plate})")
    
    print(f"\n✨ {migrated} vehículos migrados de {len(vehicles)} totales")
    return migrated


async def migrate_reservations(db_session, mongodb_client):
    """Migrar reservaciones de SQLite a MongoDB"""
    print("\n🔄 Migrando reservaciones...")
    
    reservations = db_session.query(SQLReservation).all()
    migrated = 0
    skipped = 0
    
    for sql_reservation in reservations:
        # Obtener IDs MongoDB correspondientes
        sql_user = db_session.query(SQLUser).filter(SQLUser.id == sql_reservation.user_id).first()
        sql_vehicle = db_session.query(SQLVehicle).filter(SQLVehicle.id == sql_reservation.vehicle_id).first()
        
        if not sql_user or not sql_vehicle:
            print(f"  ⚠️  Reservación {sql_reservation.id} tiene referencias inválidas, omitiendo...")
            skipped += 1
            continue
        
        # Buscar usuario y vehículo en MongoDB
        mongo_user = await User.find_one(User.email == sql_user.email)
        mongo_vehicle = await Vehicle.find_one(Vehicle.plate == sql_vehicle.plate)
        
        if not mongo_user or not mongo_vehicle:
            print(f"  ⚠️  No se encontraron usuario o vehículo en MongoDB para reservación {sql_reservation.id}")
            skipped += 1
            continue
        
        # Crear reservación MongoDB
        mongo_reservation = Reservation(
            user_id=str(mongo_user.id),
            vehicle_id=str(mongo_vehicle.id),
            start_date=sql_reservation.start_date,
            end_date=sql_reservation.end_date,
            pickup_location=sql_reservation.pickup_location,
            return_location=sql_reservation.return_location,
            total_days=sql_reservation.total_days,
            price_per_day=float(sql_reservation.price_per_day),
            total_price=float(sql_reservation.total_price),
            status=ReservationStatus(sql_reservation.status),
            notes=sql_reservation.notes,
            admin_notes=sql_reservation.admin_notes,
            created_at=sql_reservation.created_at,
            updated_at=sql_reservation.updated_at,
            cancelled_at=sql_reservation.cancelled_at
        )
        
        await mongo_reservation.insert()
        migrated += 1
        print(f"  ✅ Migrado: Reservación {sql_reservation.id}")
    
    print(f"\n✨ {migrated} reservaciones migradas de {len(reservations)} totales ({skipped} omitidas)")
    return migrated


async def migrate_password_reset_tokens(db_session, mongodb_client):
    """Migrar tokens de reseteo de contraseña"""
    print("\n🔄 Migrando tokens de reseteo...")
    
    tokens = db_session.query(SQLPasswordResetToken).all()
    migrated = 0
    
    for sql_token in tokens:
        # Obtener usuario correspondiente
        sql_user = db_session.query(SQLUser).filter(SQLUser.id == sql_token.user_id).first()
        
        if not sql_user:
            continue
        
        mongo_user = await User.find_one(User.email == sql_user.email)
        if not mongo_user:
            continue
        
        # Crear token MongoDB
        mongo_token = PasswordResetToken(
            user_id=str(mongo_user.id),
            token_hash=sql_token.token_hash,
            expires_at=sql_token.expires_at,
            used=sql_token.used,
            created_at=sql_token.created_at
        )
        
        await mongo_token.insert()
        migrated += 1
    
    print(f"\n✨ {migrated} tokens migrados de {len(tokens)} totales")
    return migrated


async def main():
    """Función principal de migración"""
    print("=" * 60)
    print("🚀 MIGRACIÓN DE DATOS: SQLite → MongoDB")
    print("=" * 60)
    
    # Conectar a SQLite
    print("\n📦 Conectando a SQLite...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    
    # Conectar a MongoDB
    print("📦 Conectando a MongoDB...")
    mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    
    try:
        # Inicializar Beanie
        await init_beanie(
            database=mongodb_client[MONGODB_DATABASE],
            document_models=[User, Vehicle, Reservation, PasswordResetToken]
        )
        print(f"✅ Conectado a MongoDB: {MONGODB_DATABASE}")
        
        # Realizar migraciones
        total_users = await migrate_users(db_session, mongodb_client)
        total_vehicles = await migrate_vehicles(db_session, mongodb_client)
        total_reservations = await migrate_reservations(db_session, mongodb_client)
        total_tokens = await migrate_password_reset_tokens(db_session, mongodb_client)
        
        # Resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE MIGRACIÓN")
        print("=" * 60)
        print(f"✅ Usuarios migrados:      {total_users}")
        print(f"✅ Vehículos migrados:     {total_vehicles}")
        print(f"✅ Reservaciones migradas: {total_reservations}")
        print(f"✅ Tokens migrados:        {total_tokens}")
        print("=" * 60)
        print("\n🎉 ¡Migración completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cerrar conexiones
        db_session.close()
        mongodb_client.close()
        print("\n👋 Conexiones cerradas")


if __name__ == "__main__":
    asyncio.run(main())
