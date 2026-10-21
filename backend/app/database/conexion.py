"""
Módulo de conexión a la base de datos PostgreSQL mediante SQLAlchemy.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker


# Carga las variables del archivo .env
load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "pc_builder_db")


# Las credenciales obligatorias no deben quedar escritas en el código.
variables_requeridas = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}

variables_faltantes = [
    nombre
    for nombre, valor in variables_requeridas.items()
    if not valor
]

if variables_faltantes:
    raise RuntimeError(
        "Faltan variables de entorno requeridas: "
        + ", ".join(variables_faltantes)
    )


# URL.create evita problemas si la contraseña contiene caracteres especiales.
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


# Motor compartido por los repositorios.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# Fábrica de sesiones.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Base utilizada por los modelos ORM.
Base = declarative_base()


def get_db():
    """
    Genera una sesión de base de datos y garantiza su cierre.

    Puede utilizarse como dependencia en FastAPI.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
