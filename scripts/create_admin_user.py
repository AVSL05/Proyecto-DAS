"""
Script para crear un usuario administrador en MongoDB
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.mongodb_models import User
from app.security import hash_password

async def create_admin():
    # Conectar a MongoDB usando la configuración común
    from app.mongodb import MONGODB_URL, DATABASE_NAME
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Inicializar Beanie
    await init_beanie(database=db, document_models=[User])
    
    # Datos del administrador
    email = "admin@cuidadopug.com"
    password = "Admin2026!"
    
    # Verificar si ya existe
    existing_user = await User.find_one(User.email == email)
    if existing_user:
        print(f"⚠️  El usuario {email} ya existe.")
        print(f"Email: {email}")
        print(f"Contraseña: {password}")
        print(f"Rol: {existing_user.role}")
        return
    
    # Crear nuevo usuario admin
    hashed_password = hash_password(password)
    admin_user = User(
        email=email,
        full_name="Administrador Principal",
        password_hash=hashed_password,
        phone="+52 81 1234 5678",
        role="administrativo"
    )
    
    await admin_user.insert()
    
    print("✅ Usuario administrador creado exitosamente!")
    print("=" * 50)
    print(f"Email: {email}")
    print(f"Contraseña: {password}")
    print(f"Rol: administrativo")
    print("=" * 50)
    print("\nPuedes iniciar sesión en: http://127.0.0.1:8000/login")

if __name__ == "__main__":
    asyncio.run(create_admin())
