"""
Script para eliminar el usuario admin anterior y crear uno correcto
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.mongodb_models import User, UserRole
from app.security import hash_password

async def recreate_admin():
    # Conectar a MongoDB - Usar la misma base de datos que el servidor
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.proyecto_das_db  # Base de datos correcta
    
    # Inicializar Beanie
    await init_beanie(database=db, document_models=[User])
    
    # Datos del administrador
    email = "admin@cuidadopug.com"
    password = "Admin2026!"
    
    # Eliminar usuario anterior si existe
    existing_user = await User.find_one(User.email == email)
    if existing_user:
        await existing_user.delete()
        print(f"🗑️  Usuario anterior eliminado")
    
    # Crear nuevo usuario admin con campos correctos
    hashed_password = hash_password(password)
    admin_user = User(
        email=email,
        full_name="Administrador Principal",
        password_hash=hashed_password,
        phone="+52 81 1234 5678",
        role=UserRole.ADMIN  # Usar el Enum directamente
    )
    
    await admin_user.insert()
    
    print("✅ Usuario administrador creado exitosamente!")
    print("=" * 50)
    print(f"Email: {email}")
    print(f"Contraseña: {password}")
    print(f"Rol: {admin_user.role.value}")
    print("=" * 50)
    print("\nPuedes iniciar sesión en: http://127.0.0.1:8000/login")

if __name__ == "__main__":
    asyncio.run(recreate_admin())
