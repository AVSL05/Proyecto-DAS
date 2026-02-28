"""
Script para agregar la tabla saved_payment_methods a la base de datos.
Migración necesaria para la funcionalidad de métodos de pago guardados.
"""

from app.db import engine, Base
from app.db_models import SavedPaymentMethod
from sqlalchemy import inspect

def migrate_payment_methods_table():
    """Crea la tabla saved_payment_methods si no existe"""
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'saved_payment_methods' in existing_tables:
        print("✅ La tabla 'saved_payment_methods' ya existe.")
        return
    
    print("🔧 Creando tabla 'saved_payment_methods'...")
    
    # Crear solo la tabla SavedPaymentMethod
    SavedPaymentMethod.__table__.create(engine, checkfirst=True)
    
    print("✅ Tabla 'saved_payment_methods' creada exitosamente.")
    print("\nColumnas creadas:")
    print("  - id (Integer, PK)")
    print("  - user_id (Integer, FK)")
    print("  - card_type (String)")
    print("  - card_holder (String)")
    print("  - card_last4 (String)")
    print("  - expiry_month (String)")
    print("  - expiry_year (String)")
    print("  - is_default (Boolean)")
    print("  - is_active (Boolean)")
    print("  - created_at (DateTime)")
    print("  - updated_at (DateTime)")

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Agregar tabla saved_payment_methods")
    print("=" * 60)
    
    try:
        migrate_payment_methods_table()
        print("\n✅ Migración completada exitosamente.")
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
