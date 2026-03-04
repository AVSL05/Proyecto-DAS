"""
Script para verificar el usuario administrador en MongoDB
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.mongodb_models import User
from app.security import verify_password

async def check_admin():
    # Conectar a MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cuidado_pug
    
    # Inicializar Beanie
    await init_beanie(database=db, document_models=[User])
    
    email = "admin@cuidadopug.com"
    password = "Admin2026!"
    
    # Buscar usuario
    user = await User.find_one(User.email == email)
    
    if not user:
        print(f"❌ Usuario {email} NO encontrado en la base de datos")
        return
    
    print("✅ Usuario encontrado:")
    print(f"  ID: {user.id}")
    print(f"  Email: {user.email}")
    print(f"  Nombre: {user.full_name}")
    print(f"  Rol: {user.role}")
    print(f"  Hash password: {user.password_hash[:50]}...")
    
    # Verificar password
    is_valid = verify_password(password, user.password_hash)
    if is_valid:
        print(f"\n✅ La contraseña '{password}' es VÁLIDA")
    else:
        print(f"\n❌ La contraseña '{password}' NO es válida")
    
    # Mostrar todos los usuarios
    print("\n" + "="*50)
    print("Todos los usuarios en la base de datos:")
    all_users = await User.find_all().to_list()
    for u in all_users:
        print(f"  - {u.email} | {u.full_name} | {u.role}")

if __name__ == "__main__":
    asyncio.run(check_admin())
