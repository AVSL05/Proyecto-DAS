"""
Script para migrar la base de datos y agregar las columnas de Google OAuth
Compatible con SQLite
"""
from app.db import engine
from sqlalchemy import text

def migrate_database():
    """Agrega las columnas necesarias para Google OAuth si no existen"""
    
    with engine.connect() as conn:
        try:
            # Agregar columna google_id (sin UNIQUE porque SQLite no lo soporta en ALTER TABLE)
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN google_id VARCHAR(255)
                """))
                conn.commit()
                print("✅ Columna 'google_id' agregada")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️  Columna 'google_id' ya existe")
                else:
                    print(f"⚠️  Error al agregar 'google_id': {e}")
            
            # Agregar columna avatar_url
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN avatar_url VARCHAR(500)
                """))
                conn.commit()
                print("✅ Columna 'avatar_url' agregada")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️  Columna 'avatar_url' ya existe")
                else:
                    print(f"⚠️  Error al agregar 'avatar_url': {e}")
            
            # Crear índice en google_id para búsquedas rápidas
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_google_id 
                    ON users(google_id)
                """))
                conn.commit()
                print("✅ Índice en 'google_id' creado")
            except Exception as e:
                print(f"⚠️  Error al crear índice: {e}")
            
            print("\n✅ Migración completada exitosamente")
            print("\nℹ️  Nota: Para SQLite, las columnas phone y password_hash ya permiten NULL por defecto")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando migración de base de datos...")
    migrate_database()
