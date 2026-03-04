"""
Script para limpiar (drop) la base de datos de MongoDB configurada y opcionalmente
sembrar datos iniciales.
"""
import asyncio
from app.mongodb import connect_to_mongo, get_database, DATABASE_NAME

async def reset_database():
    # Conectar al cliente
    await connect_to_mongo()
    db = get_database()

    print(f"🔄 Eliminando base de datos '{DATABASE_NAME}'... (se perderán todos los datos)")
    await db.client.drop_database(DATABASE_NAME)
    print("✅ Base de datos eliminada.")

    # volver a conectar para re-inicializar colecciones vacías
    await connect_to_mongo()
    print("✅ Reconectado después de borrar.")

    # opcional: puedes ejecutar aquí scripts de seed si los tienes disponibles,
    # p.ej. import seed_vehicles y seed_admin_data si la aplicación los provee.

if __name__ == "__main__":
    asyncio.run(reset_database())
