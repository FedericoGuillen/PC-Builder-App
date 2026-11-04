"""
Esquemas de validación de Pydantic (DTOs) para la autenticación de usuarios.

Definen los contratos de datos de entrada y salida para el registro,
el inicio de sesión y la entrega del token de acceso.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalizar_email(valor: str) -> str:
    """Valida de forma básica el email y lo normaliza a minúsculas."""

    email = valor.strip().lower()
    partes = email.split("@")

    if (
        len(partes) != 2
        or not partes[0]
        or not partes[1]
        or "." not in partes[1]
    ):
        raise ValueError("El email no tiene un formato válido.")

    return email


class UsuarioCreate(BaseModel):
    """DTO de Entrada: datos necesarios para registrar un usuario."""

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre del usuario.",
    )
    apellido: Optional[str] = Field(
        None,
        max_length=100,
        description="Apellido del usuario (opcional).",
    )
    email: str = Field(
        ...,
        max_length=255,
        description="Email único del usuario; se utiliza para iniciar sesión.",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Contraseña en texto plano; se almacena hasheada.",
    )

    @field_validator("nombre")
    @classmethod
    def normalizar_nombre(cls, valor: str) -> str:
        nombre = valor.strip()

        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")

        return nombre

    @field_validator("apellido")
    @classmethod
    def normalizar_apellido(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None

        apellido = valor.strip()

        return apellido or None

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        return _normalizar_email(valor)

    @field_validator("password")
    @classmethod
    def validar_longitud_password(cls, valor: str) -> str:
        # bcrypt solo procesa los primeros 72 bytes de la contraseña.
        if len(valor.encode("utf-8")) > 72:
            raise ValueError(
                "La contraseña no puede superar los 72 bytes."
            )

        return valor

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Alex",
                "apellido": "García",
                "email": "alex@correo.com",
                "password": "MiClaveSegura123",
            }
        }
    )


class UsuarioLogin(BaseModel):
    """DTO de Entrada: credenciales para iniciar sesión."""

    email: str = Field(
        ...,
        max_length=255,
        description="Email registrado del usuario.",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=72,
        description="Contraseña del usuario.",
    )

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        return _normalizar_email(valor)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "alex@correo.com",
                "password": "MiClaveSegura123",
            }
        }
    )


class UsuarioResponse(BaseModel):
    """DTO de Salida: datos públicos de un usuario."""

    id_usuario: int
    nombre: str
    apellido: Optional[str] = None
    email: str
    fecha_registro: datetime
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class RegistroResponse(BaseModel):
    """DTO de Salida: confirmación del registro de un usuario."""

    mensaje: str = "Usuario registrado correctamente."
    usuario: UsuarioResponse


class TokenResponse(BaseModel):
    """DTO de Salida: token de acceso y datos de sesión del usuario."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        ...,
        description="Cantidad de segundos de validez del token.",
    )
    usuario: UsuarioResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "usuario": {
                    "id_usuario": 1,
                    "nombre": "Alex",
                    "apellido": "García",
                    "email": "alex@correo.com",
                    "fecha_registro": "2026-11-03T10:00:00",
                    "activo": True,
                },
            }
        }
    )
