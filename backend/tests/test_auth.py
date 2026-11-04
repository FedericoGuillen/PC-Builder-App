from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.controllers.auth_controller as auth_controller
from app.schemas.auth import UsuarioCreate, UsuarioLogin
from app.security import (
    crear_access_token,
    decodificar_access_token,
    hash_password,
    verify_password,
)
from app.services.auth_service import (
    AuthService,
    CredencialesInvalidasError,
    UsuarioDuplicadoError,
)


# ====================================================================
# Tests de hashing y tokens
# ====================================================================

def test_hash_password_no_guarda_texto_plano():
    """El hash debe ser distinto de la contraseña y verificable."""

    password = "MiClaveSegura123"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("OtraClave123", password_hash) is False


def test_verify_password_con_hash_invalido():
    """Un hash inválido no debe romper la verificación."""

    assert verify_password("MiClaveSegura123", "hash-invalido") is False


def test_crear_y_decodificar_access_token():
    """El token debe conservar los datos y poder decodificarse."""

    token = crear_access_token({"sub": "7", "email": "alex@correo.com"})
    payload = decodificar_access_token(token)

    assert payload["sub"] == "7"
    assert payload["email"] == "alex@correo.com"
    assert "exp" in payload


# ====================================================================
# Tests del servicio de autenticación
# ====================================================================

def test_registrar_usuario_hashea_la_password():
    """El servicio debe hashear la contraseña antes de guardarla."""

    repositorio = MagicMock()
    repositorio.obtener_por_email.return_value = None
    repositorio.crear.return_value = {
        "id_usuario": 1,
        "nombre": "Alex",
        "apellido": "García",
        "email": "alex@correo.com",
        "fecha_registro": datetime(2026, 11, 3, 10, 0, 0),
        "activo": True,
    }

    servicio = AuthService(usuario_repository=repositorio)
    datos = UsuarioCreate(
        nombre="Alex",
        apellido="García",
        email="Alex@Correo.com",
        password="MiClaveSegura123",
    )

    usuario = servicio.registrar_usuario(datos)

    assert usuario["id_usuario"] == 1
    repositorio.obtener_por_email.assert_called_once_with("alex@correo.com")

    parametros = repositorio.crear.call_args.kwargs
    assert parametros["email"] == "alex@correo.com"
    assert parametros["password_hash"] != "MiClaveSegura123"
    assert verify_password(
        "MiClaveSegura123",
        parametros["password_hash"],
    ) is True


def test_registrar_usuario_duplicado():
    """Si el email ya existe debe lanzar UsuarioDuplicadoError."""

    repositorio = MagicMock()
    repositorio.obtener_por_email.return_value = {"id_usuario": 1}

    servicio = AuthService(usuario_repository=repositorio)
    datos = UsuarioCreate(
        nombre="Alex",
        email="alex@correo.com",
        password="MiClaveSegura123",
    )

    with pytest.raises(UsuarioDuplicadoError):
        servicio.registrar_usuario(datos)


def test_iniciar_sesion_devuelve_token_y_datos_usuario():
    """Con credenciales válidas debe devolver un token y datos públicos."""

    password_hash = hash_password("MiClaveSegura123")
    repositorio = MagicMock()
    repositorio.obtener_por_email.return_value = {
        "id_usuario": 5,
        "nombre": "Alex",
        "apellido": "García",
        "email": "alex@correo.com",
        "password_hash": password_hash,
        "fecha_registro": datetime(2026, 11, 3, 10, 0, 0),
        "activo": True,
    }

    servicio = AuthService(usuario_repository=repositorio)
    sesion = servicio.iniciar_sesion(
        UsuarioLogin(
            email="alex@correo.com",
            password="MiClaveSegura123",
        )
    )

    assert sesion["token_type"] == "bearer"
    assert sesion["expires_in"] > 0
    assert "password_hash" not in sesion["usuario"]
    assert decodificar_access_token(sesion["access_token"])["sub"] == "5"


def test_iniciar_sesion_con_password_incorrecta():
    """Con una contraseña incorrecta debe rechazar el inicio de sesión."""

    repositorio = MagicMock()
    repositorio.obtener_por_email.return_value = {
        "id_usuario": 5,
        "email": "alex@correo.com",
        "password_hash": hash_password("MiClaveSegura123"),
        "activo": True,
    }

    servicio = AuthService(usuario_repository=repositorio)

    with pytest.raises(CredencialesInvalidasError):
        servicio.iniciar_sesion(
            UsuarioLogin(email="alex@correo.com", password="Incorrecta123")
        )


# ====================================================================
# Tests de los endpoints
# ====================================================================

app = FastAPI()
app.include_router(auth_controller.router)
client = TestClient(app)


def test_endpoint_registro(monkeypatch):
    """POST /register debe responder 201 con la confirmación del alta."""

    monkeypatch.setattr(
        auth_controller.auth_service,
        "registrar_usuario",
        lambda datos: {
            "id_usuario": 1,
            "nombre": datos.nombre,
            "apellido": datos.apellido,
            "email": datos.email,
            "fecha_registro": datetime(2026, 11, 3, 10, 0, 0),
            "activo": True,
        },
    )

    respuesta = client.post(
        "/api/v1/auth/register",
        json={
            "nombre": "Alex",
            "apellido": "García",
            "email": "Alex@Correo.com",
            "password": "MiClaveSegura123",
        },
    )

    assert respuesta.status_code == 201
    data = respuesta.json()
    assert data["mensaje"] == "Usuario registrado correctamente."
    assert data["usuario"]["email"] == "alex@correo.com"


def test_endpoint_registro_email_duplicado(monkeypatch):
    """POST /register debe responder 409 si el email ya existe."""

    def lanzar_error(datos):
        raise UsuarioDuplicadoError(
            "Ya existe un usuario registrado con ese email."
        )

    monkeypatch.setattr(
        auth_controller.auth_service,
        "registrar_usuario",
        lanzar_error,
    )

    respuesta = client.post(
        "/api/v1/auth/register",
        json={
            "nombre": "Alex",
            "email": "alex@correo.com",
            "password": "MiClaveSegura123",
        },
    )

    assert respuesta.status_code == 409


def test_endpoint_login(monkeypatch):
    """POST /login debe devolver el token de acceso."""

    monkeypatch.setattr(
        auth_controller.auth_service,
        "iniciar_sesion",
        lambda datos: {
            "access_token": "token-de-prueba",
            "token_type": "bearer",
            "expires_in": 3600,
            "usuario": {
                "id_usuario": 1,
                "nombre": "Alex",
                "apellido": "García",
                "email": "alex@correo.com",
                "fecha_registro": datetime(2026, 11, 3, 10, 0, 0),
                "activo": True,
            },
        },
    )

    respuesta = client.post(
        "/api/v1/auth/login",
        json={
            "email": "alex@correo.com",
            "password": "MiClaveSegura123",
        },
    )

    assert respuesta.status_code == 200
    data = respuesta.json()
    assert data["access_token"] == "token-de-prueba"
    assert data["token_type"] == "bearer"


def test_endpoint_login_credenciales_invalidas(monkeypatch):
    """POST /login debe responder 401 con credenciales incorrectas."""

    def lanzar_error(datos):
        raise CredencialesInvalidasError("Email o contraseña incorrectos.")

    monkeypatch.setattr(
        auth_controller.auth_service,
        "iniciar_sesion",
        lanzar_error,
    )

    respuesta = client.post(
        "/api/v1/auth/login",
        json={
            "email": "alex@correo.com",
            "password": "Incorrecta123",
        },
    )

    assert respuesta.status_code == 401
