"""
Utilidades de seguridad para la autenticación.

Centraliza el hashing de contraseñas con bcrypt (a través de passlib)
y la creación/validación de tokens JWT.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext


load_dotenv()


# Contexto de hashing. bcrypt genera un salt aleatorio por contraseña.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Clave de firma de los tokens. En producción debe definirse en el .env.
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "buildlab-clave-de-desarrollo-cambiar-en-produccion",
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "60")
)


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de una contraseña en texto plano."""

    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Compara una contraseña en texto plano con su hash almacenado."""

    try:
        return pwd_context.verify(password, password_hash)
    except (TypeError, ValueError):
        # Hash inválido o contraseña fuera de los límites de bcrypt.
        return False


def crear_access_token(datos: Dict[str, Any]) -> str:
    """Crea un token JWT firmado con los datos indicados."""

    ahora = datetime.now(timezone.utc)
    payload = {
        **datos,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decodificar_access_token(token: str) -> Dict[str, Any]:
    """
    Valida la firma y la expiración de un token JWT.

    Lanza jwt.PyJWTError si el token es inválido o expiró.
    """

    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
