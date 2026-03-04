"""
Script para insertar datos de prueba para el panel administrativo
"""
import asyncio
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "proyecto_das_db")


async def seed_admin_data():
    """Insertar datos de prueba para el panel administrativo"""
    # Conectar a MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    
    from app.mongodb_models import (
        User, Vehicle, Reservation, Payment, SupportTicket,
        PaymentStatus, ReservationStatus, UserRole, VehicleStatus
    )
    
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[
            User, Vehicle, Reservation, Payment, SupportTicket
        ]
    )
    
    print("🔄 Insertando datos de prueba para el panel administrativo...")
    
    # Obtener usuarios y vehículos existentes
    users = await User.find_all().to_list()
    vehicles = await Vehicle.find_all().to_list()
    reservations = await Reservation.find_all().to_list()
    
    if not users:
        print("⚠️  No hay usuarios en la base de datos. Ejecuta seed_vehicles.py primero.")
        return
    
    if not vehicles:
        print("⚠️  No hay vehículos en la base de datos. Ejecuta seed_vehicles.py primero.")
        return
    
    # Crear algunos pagos de ejemplo
    payments_created = 0
    for i, reservation in enumerate(reservations[:10]):
        # Verificar si ya existe un pago para esta reservación
        existing_payment = await Payment.find_one(Payment.reservation_id == str(reservation.id))
        if existing_payment:
            continue
        
        # Crear pago
        if i % 3 == 0:
            status = PaymentStatus.ACCEPTED
        elif i % 3 == 1:
            status = PaymentStatus.PENDING
        else:
            status = PaymentStatus.ACCEPTED
        
        payment = Payment(
            reservation_id=str(reservation.id),
            user_id=str(reservation.user_id),
            amount=float(reservation.total_price),
            method=["efectivo", "tarjeta", "transferencia"][i % 3],
            status=status,
            created_at=reservation.created_at - timedelta(days=1),
        )
        await payment.insert()
        payments_created += 1
    
    print(f"✅ {payments_created} pagos creados")
    
    # Crear tickets de soporte de ejemplo
    tickets_created = 0
    categories = ["cancelacion", "cambio_fecha", "problema_vehiculo", "consulta", "reembolso"]
    priorities = ["low", "medium", "high"]
    statuses = ["abierto", "cerrado"]
    
    for i in range(min(15, len(users))):
        user = users[i % len(users)]
        reservation = reservations[i % len(reservations)] if reservations else None
        
        # Verificar si ya existe un ticket similar
        existing_ticket = await SupportTicket.find_one({
            "user_id": str(user.id),
            "subject": f"Consulta {i+1}"
        })
        if existing_ticket:
            continue
        
        ticket = SupportTicket(
            user_id=str(user.id),
            reservation_id=str(reservation.id) if reservation else None,
            subject=f"Consulta {i+1}: {categories[i % len(categories)]}",
            message=f"Este es un ticket de prueba para {categories[i % len(categories)]}. Cliente requiere asistencia.",
            category=categories[i % len(categories)],
            priority=priorities[i % len(priorities)],
            status=statuses[i % 2],
            created_at=datetime.now(timezone.utc) - timedelta(days=i),
            updated_at=datetime.now(timezone.utc) - timedelta(days=max(0, i-2)),
        )
        
        if ticket.status == "cerrado":
            ticket.admin_response = "Ticket resuelto satisfactoriamente."
            ticket.resolved_at = datetime.now(timezone.utc) - timedelta(days=max(0, i-1))
        
        await ticket.insert()
        tickets_created += 1
    
    print(f"✅ {tickets_created} tickets de soporte creados")
    
    # Estadísticas finales
    total_payments = await Payment.count()
    total_tickets = await SupportTicket.count()
    total_reservations = await Reservation.count()
    total_users = await User.count()
    total_vehicles = await Vehicle.count()
    
    print("\n📊 Estadísticas de la base de datos:")
    print(f"   👥 Usuarios: {total_users}")
    print(f"   🚗 Vehículos: {total_vehicles}")
    print(f"   📝 Reservaciones: {total_reservations}")
    print(f"   💳 Pagos: {total_payments}")
    print(f"   🎫 Tickets: {total_tickets}")
    
    print("\n✅ ¡Datos de prueba insertados exitosamente!")
    print("\n🚀 Ahora puedes iniciar el servidor y acceder al panel administrativo")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_admin_data())
