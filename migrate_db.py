"""
Script de migracion para columnas de autenticacion y rol de usuario.
Compatible con SQLite.
"""
from sqlalchemy import text

from app.db import engine


def migrate_database():
    """Agrega columnas necesarias si no existen."""
    with engine.connect() as conn:
        try:
            try:
                conn.execute(
                    text(
                        """
                        ALTER TABLE users
                        ADD COLUMN google_id VARCHAR(255)
                        """
                    )
                )
                conn.commit()
                print("Columna 'google_id' agregada")
            except Exception as exc:
                if "duplicate column name" in str(exc).lower():
                    print("Columna 'google_id' ya existe")
                else:
                    print(f"Error al agregar 'google_id': {exc}")

            try:
                conn.execute(
                    text(
                        """
                        ALTER TABLE users
                        ADD COLUMN avatar_url VARCHAR(500)
                        """
                    )
                )
                conn.commit()
                print("Columna 'avatar_url' agregada")
            except Exception as exc:
                if "duplicate column name" in str(exc).lower():
                    print("Columna 'avatar_url' ya existe")
                else:
                    print(f"Error al agregar 'avatar_url': {exc}")

            try:
                conn.execute(
                    text(
                        """
                        ALTER TABLE users
                        ADD COLUMN role VARCHAR(30) NOT NULL DEFAULT 'cliente'
                        """
                    )
                )
                conn.commit()
                print("Columna 'role' agregada")
            except Exception as exc:
                if "duplicate column name" in str(exc).lower():
                    print("Columna 'role' ya existe")
                else:
                    print(f"Error al agregar 'role': {exc}")

            try:
                conn.execute(
                    text(
                        """
                        UPDATE users
                        SET role = 'cliente'
                        WHERE role IS NULL OR TRIM(role) = ''
                        """
                    )
                )
                conn.commit()
                print("Roles existentes normalizados")
            except Exception as exc:
                print(f"Error al normalizar roles: {exc}")

            try:
                conn.execute(
                    text(
                        """
                        CREATE INDEX IF NOT EXISTS idx_users_google_id
                        ON users(google_id)
                        """
                    )
                )
                conn.commit()
                print("Indice de google_id creado")
            except Exception as exc:
                print(f"Error al crear indice de google_id: {exc}")

            try:
                conn.execute(
                    text(
                        """
                        CREATE INDEX IF NOT EXISTS idx_users_role
                        ON users(role)
                        """
                    )
                )
                conn.commit()
                print("Indice de role creado")
            except Exception as exc:
                print(f"Error al crear indice de role: {exc}")

            print("Migracion completada")
        except Exception as exc:
            print(f"Error general durante la migracion: {exc}")


if __name__ == "__main__":
    print("Iniciando migracion de base de datos...")
    migrate_database()
