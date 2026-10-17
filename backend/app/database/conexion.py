"""
Módulo de conexión a la base de datos PostgreSQL mediante SQLAlchemy.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cargar variables de entorno desde el archivo .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "pc_builder_db")

# Especificamos +psycopg2 para indicarle explícitamente el driver a SQLAlchemy
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Motor de conexión a PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Fábrica de sesiones ORM
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase Base declarativa
Base = declarative_base()


def get_db():
    """Generador de sesiones para inyección de dependencias en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()