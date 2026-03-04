"""
Script para cambiar la contraseña de un usuario
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.mongodb_models import User
from app.security import hash_password, verify_password

async def reset_password():
    # Conectar a MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.proyecto_das_db
    
    # Inicializar Beanie
    await init_beanie(database=db, document_models=[User])
    
    print("=" * 70)
    print("CAMBIAR CONTRASEÑA DE USUARIO")
    print("=" * 70)
    
    # Mostrar usuarios disponibles
    all_users = await User.find_all().to_list()
    print(f"\nUsuarios disponibles:")
    for idx, user in enumerate(all_users, 1):
        print(f"  {idx}. {user.email} - {user.full_name} ({user.role.value})")
    
    # Seleccionar usuario (voy a usar el primero como ejemplo)
    email_to_reset = "papusaurio@gmail.com"  # Cambia esto por el email que necesites
    new_password = "Papu1234!"  # Nueva contraseña
    
    user = await User.find_one(User.email == email_to_reset)
    
    if not user:
        print(f"\n❌ Usuario {email_to_reset} no encontrado")
        return
    
    # Cambiar contraseña
    user.password_hash = hash_password(new_password)
    await user.save()
    
    print(f"\n✅ Contraseña actualizada para: {user.email}")
    print(f"   Nueva contraseña: {new_password}")
    print(f"   Puedes iniciar sesión con estas credenciales")
    
    # Verificar
    saved_user = await User.find_one(User.email == email_to_reset)
    is_valid = verify_password(new_password, saved_user.password_hash)
    
    if is_valid:
        print(f"\n✅ Verificación exitosa - la contraseña funciona correctamente")
    else:
        print(f"\n❌ ERROR en la verificación")

if __name__ == "__main__":
    asyncio.run(reset_password())
