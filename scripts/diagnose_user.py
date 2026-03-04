"""
Diagnosticar el problema de registro e inicio de sesión
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.mongodb_models import User
from app.security import hash_password, verify_password

async def diagnose():
    # Conectar a MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.proyecto_das_db
    
    # Inicializar Beanie
    await init_beanie(database=db, document_models=[User])
    
    print("=" * 70)
    print("DIAGNÓSTICO DE USUARIOS EN LA BASE DE DATOS")
    print("=" * 70)
    
    # Listar todos los usuarios
    all_users = await User.find_all().to_list()
    
    if not all_users:
        print("\n❌ NO HAY USUARIOS EN LA BASE DE DATOS")
        return
    
    print(f"\n✅ Total de usuarios: {len(all_users)}")
    print("\n" + "-" * 70)
    
    for idx, user in enumerate(all_users, 1):
        print(f"\n👤 Usuario #{idx}:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Nombre: {user.full_name}")
        print(f"   Teléfono: {user.phone}")
        print(f"   Rol: {user.role}")
        print(f"   Google ID: {user.google_id}")
        print(f"   Password Hash: {user.password_hash[:50] if user.password_hash else 'NO TIENE'}...")
        
        # Probar contraseña de prueba
        test_password = "Test1234"
        if user.password_hash:
            is_valid = verify_password(test_password, user.password_hash)
            print(f"   ¿Contraseña '{test_password}' válida?: {is_valid}")
        else:
            print(f"   ⚠️ Usuario sin contraseña (probablemente login con Google)")
    
    print("\n" + "=" * 70)
    
    # Probar crear un usuario de prueba y verificar
    print("\n🧪 PRUEBA DE REGISTRO Y VERIFICACIÓN:")
    print("-" * 70)
    
    test_email = "test_diagnostic@test.com"
    test_pwd = "TestPass123"
    
    # Eliminar usuario de prueba si existe
    existing = await User.find_one(User.email == test_email)
    if existing:
        await existing.delete()
        print(f"🗑️  Usuario de prueba anterior eliminado")
    
    # Crear usuario de prueba
    print(f"\n📝 Creando usuario de prueba:")
    print(f"   Email: {test_email}")
    print(f"   Contraseña: {test_pwd}")
    
    hashed = hash_password(test_pwd)
    print(f"   Hash generado: {hashed[:50]}...")
    
    test_user = User(
        email=test_email,
        full_name="Usuario de Prueba",
        password_hash=hashed,
        phone="1234567890",
        role="cliente"
    )
    
    await test_user.insert()
    print(f"   ✅ Usuario creado con ID: {test_user.id}")
    
    # Verificar que se guardó correctamente
    saved_user = await User.find_one(User.email == test_email)
    if saved_user:
        print(f"\n✅ Usuario recuperado de la base de datos")
        print(f"   Hash en DB: {saved_user.password_hash[:50]}...")
        
        # Verificar contraseña
        is_valid = verify_password(test_pwd, saved_user.password_hash)
        print(f"\n🔐 Verificación de contraseña:")
        print(f"   ¿Contraseña '{test_pwd}' válida?: {is_valid}")
        
        if is_valid:
            print(f"   ✅ ¡FUNCIONA CORRECTAMENTE!")
        else:
            print(f"   ❌ ERROR: La contraseña no se verifica correctamente")
        
        # Limpiar
        await saved_user.delete()
        print(f"\n🗑️  Usuario de prueba eliminado")
    else:
        print(f"\n❌ ERROR: No se pudo recuperar el usuario recién creado")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(diagnose())
