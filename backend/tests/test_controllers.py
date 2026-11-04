import pytest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.controllers.pc_controller as pc_controller
from app.controllers.pc_controller import router


# Creamos una aplicación FastAPI al vuelo solo para montar las rutas de prueba
app = FastAPI()
app.include_router(router)

# Instanciamos el cliente de pruebas
client = TestClient(app)


# Componentes simulados que devuelve el repositorio para no depender de la BD.
COMPONENTES = {
    1: {
        "id_componente": 1,
        "id_tipo": 1,
        "id_marca": 1,
        "nombre": "Ryzen 5 7600",
        "categoria": "Procesador",
        "marca": "AMD",
        "consumo_watts": 65,
        "precio_referencia": 250.0,
        "stock": 5,
        "especificaciones": {"socket": "AM5"},
    },
    2: {
        "id_componente": 2,
        "id_tipo": 2,
        "id_marca": 2,
        "nombre": "Placa Madre B650",
        "categoria": "Placa Madre",
        "marca": "ASUS",
        "consumo_watts": 30,
        "precio_referencia": 150.0,
        "stock": 5,
        "especificaciones": {"socket": "AM5"},
    },
    3: {
        "id_componente": 3,
        "id_tipo": 3,
        "id_marca": 3,
        "nombre": "Fuente 600W",
        "categoria": "Fuente de Poder",
        "marca": "Corsair",
        "consumo_watts": 0,
        "precio_referencia": 80.0,
        "stock": 5,
        "especificaciones": {"watts": 600},
    },
    4: {
        "id_componente": 4,
        "id_tipo": 1,
        "id_marca": 4,
        "nombre": "Intel Core i7",
        "categoria": "Procesador",
        "marca": "Intel",
        "consumo_watts": 125,
        "precio_referencia": 350.0,
        "stock": 5,
        "especificaciones": {"socket": "LGA1700"},
    },
    5: {
        "id_componente": 5,
        "id_tipo": 2,
        "id_marca": 2,
        "nombre": "Placa Madre B650",
        "categoria": "Placa Madre",
        "marca": "ASUS",
        "consumo_watts": 30,
        "precio_referencia": 150.0,
        "stock": 5,
        "especificaciones": {"socket": "AM5"},
    },
    6: {
        "id_componente": 6,
        "id_tipo": 3,
        "id_marca": 3,
        "nombre": "Fuente 100W",
        "categoria": "Fuente de Poder",
        "marca": "Corsair",
        "consumo_watts": 0,
        "precio_referencia": 20.0,
        "stock": 5,
        "especificaciones": {"watts": 100},
    },
}


def _obtener_componente_mock(id_componente):
    """Simula el repositorio devolviendo un componente por su ID."""

    return COMPONENTES.get(id_componente)


@pytest.fixture
def componentes_mock():
    """Reemplaza el acceso a la BD por componentes de prueba."""

    with patch.object(
        pc_controller.componente_repo,
        "obtener_por_id",
        side_effect=_obtener_componente_mock,
    ):
        yield


def test_validar_pc_compatible(componentes_mock):
    """Prueba el endpoint con componentes compatibles."""

    payload = {
        "id_perfil": 1,
        "componentes_ids": [1, 2, 3],
    }

    response = client.post("/api/v1/compatibilidad/validar", json=payload)

    # Validamos que HTTP sea 200 OK
    assert response.status_code == 200

    data = response.json()
    assert data["es_compatible"] is True
    assert len(data["errores"]) == 0


def test_validar_pc_incompatible(componentes_mock):
    """Prueba el endpoint enviando componentes que generen conflictos de reglas."""

    payload = {
        "id_perfil": 1,
        "componentes_ids": [4, 5, 6],
    }

    response = client.post("/api/v1/compatibilidad/validar", json=payload)

    # El status debe seguir siendo 200 porque la petición es correcta
    # (la lógica de negocio es la que "falla").
    assert response.status_code == 200

    data = response.json()
    assert data["es_compatible"] is False
    # Deben detectarse al menos 2 errores: Socket y Fuente
    assert len(data["errores"]) >= 2


def test_validar_pc_payload_invalido():
    """Prueba que Pydantic rechace peticiones con datos faltantes."""

    payload_incompleto = {
        "id_perfil": 1,
        # Falta componentes_ids
    }

    response = client.post(
        "/api/v1/compatibilidad/validar",
        json=payload_incompleto,
    )

    # FastAPI debe retornar 422 Unprocessable Entity automáticamente
    assert response.status_code == 422
    errores = response.json()["detail"]
    assert any("componentes_ids" in error["loc"] for error in errores)
