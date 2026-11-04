"""
Servicio de autenticación.

Orquesta el registro de usuarios y el inicio de sesión, aplicando
hashing de contraseñas y emisión de tokens JWT.
"""

from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import UsuarioCreate, UsuarioLogin
from app.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    crear_access_token,
    hash_password,
    verify_password,
)


class AuthError(Exception):
    """Error de negocio base del módulo de autenticación."""


class UsuarioDuplicadoError(AuthError):
    """El email ingresado ya pertenece a un usuario registrado."""


class CredencialesInvalidasError(AuthError):
    """El email no existe o la contraseña no coincide."""


class UsuarioInactivoError(AuthError):
    """El usuario existe pero su cuenta está deshabilitada."""


class AuthService:
    """Servicio de casos de uso de registro e inicio de sesión."""

    def __init__(self, usuario_repository: UsuarioRepository = None):
        self.usuario_repository = (
            usuario_repository or UsuarioRepository()
        )

    def registrar_usuario(self, datos: UsuarioCreate):
        """Registra un usuario nuevo con la contraseña hasheada."""

        if self.usuario_repository.obtener_por_email(datos.email):
            raise UsuarioDuplicadoError(
                "Ya existe un usuario registrado con ese email."
            )

        try:
            return self.usuario_repository.crear(
                nombre=datos.nombre,
                apellido=datos.apellido,
                email=datos.email,
                password_hash=hash_password(datos.password),
            )

        except ValueError as error:
            # Puede ocurrir si dos registros simultáneos usan el mismo email.
            raise UsuarioDuplicadoError(str(error)) from error

    def iniciar_sesion(self, datos: UsuarioLogin):
        """Valida las credenciales y devuelve el token y los datos de sesión."""

        usuario = self.usuario_repository.obtener_por_email(datos.email)

        if usuario is None or not verify_password(
            datos.password,
            usuario["password_hash"],
        ):
            raise CredencialesInvalidasError(
                "Email o contraseña incorrectos."
            )

        if not usuario.get("activo", False):
            raise UsuarioInactivoError(
                "La cuenta se encuentra deshabilitada."
            )

        access_token = crear_access_token(
            {
                "sub": str(usuario["id_usuario"]),
                "email": usuario["email"],
                "nombre": usuario["nombre"],
            }
        )

        usuario_publico = {
            clave: valor
            for clave, valor in usuario.items()
            if clave != "password_hash"
        }

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "usuario": usuario_publico,
        }
