"""
Configuración de MongoDB con Motor (async driver)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "proyecto_das_db")

# Cliente de MongoDB
mongodb_client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Conectar a MongoDB"""
    global mongodb_client
    mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    
    # Importar todos los modelos
    from app.mongodb_models import (
        User, PasswordResetToken, Vehicle, Reservation,
        Review, NewsletterSubscriber, Promotion
    )
    
    # Inicializar Beanie con todos los modelos
    await init_beanie(
        database=mongodb_client[DATABASE_NAME],
        document_models=[
            User,
            PasswordResetToken,
            Vehicle,
            Reservation,
            Review,
            NewsletterSubscriber,
            Promotion
        ]
    )
    print(f"✅ Conectado a MongoDB: {DATABASE_NAME}")


async def close_mongo_connection():
    """Cerrar conexión a MongoDB"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("❌ Desconectado de MongoDB")


def get_database():
    """Obtener la base de datos de MongoDB"""
    return mongodb_client[DATABASE_NAME]
