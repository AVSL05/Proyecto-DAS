from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./dev.db"  # crea dev.db en backend/

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # solo SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def ensure_user_role_column() -> None:
    """Asegura que la tabla users tenga la columna role para control de accesos."""
    with engine.connect() as conn:
        columns = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        column_names = {column[1] for column in columns}

        if "role" not in column_names:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN role VARCHAR(30) NOT NULL DEFAULT 'cliente'")
            )
            conn.commit()
        else:
            conn.execute(
                text("UPDATE users SET role = 'cliente' WHERE role IS NULL OR TRIM(role) = ''")
            )
            conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
