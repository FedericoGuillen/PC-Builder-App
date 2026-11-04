"""
Controlador de autenticación.

Expone los endpoints REST para el registro de usuarios y el inicio
de sesión.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import (
    RegistroResponse,
    TokenResponse,
    UsuarioCreate,
    UsuarioLogin,
)
from app.services.auth_service import (
    AuthService,
    CredencialesInvalidasError,
    UsuarioDuplicadoError,
    UsuarioInactivoError,
)


router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

auth_service = AuthService()


@router.post(
    "/register",
    response_model=RegistroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un usuario nuevo",
)
def registrar_usuario(datos: UsuarioCreate):
    """Crea un usuario con la contraseña hasheada y confirma el alta."""

    try:
        usuario = auth_service.registrar_usuario(datos)

        return RegistroResponse(usuario=usuario)

    except UsuarioDuplicadoError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
def iniciar_sesion(datos: UsuarioLogin):
    """Valida las credenciales y devuelve el token de acceso."""

    try:
        return auth_service.iniciar_sesion(datos)

    except CredencialesInvalidasError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    except UsuarioInactivoError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
