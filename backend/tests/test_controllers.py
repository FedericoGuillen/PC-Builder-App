import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Importamos el router directamente desde tu controlador
from app.controllers.pc_controller import router

# Creamos una aplicación FastAPI al vuelo solo para montar las rutas de prueba
app = FastAPI()
app.include_router(router)

# Instanciamos el cliente de pruebas
client = TestClient(app)

def test_validar_pc_compatible():
    """Prueba el endpoint con un payload válido y componentes compatibles."""
    payload = {
        "nombre_configuracion": "PC Master Race",
        "componentes": [
            {
                "id_componente": 1,
                "nombre": "Ryzen 5 7600",
                "tipo": "Procesador",
                "consumo_watts": 65,
                "precio": 250.0,
                "especificaciones": {"socket": "AM5"}
            },
            {
                "id_componente": 2,
                "nombre": "Placa Madre B650",
                "tipo": "Placa Madre",
                "consumo_watts": 30,
                "precio": 150.0,
                "especificaciones": {"socket": "AM5"}
            },
            {
                "id_componente": 3,
                "nombre": "Fuente 600W",
                "tipo": "Fuente de Poder",
                "consumo_watts": 0,
                "precio": 80.0,
                "especificaciones": {"watts": 600}
            }
        ]
    }

    # Hacemos el POST al endpoint
    response = client.post("/api/v1/pc/validar-compatibilidad", json=payload)

    # Validamos que HTTP sea 200 OK
    assert response.status_code == 200
    
    data = response.json()
    assert data["configuracion"] == "PC Master Race"
    assert data["resultados_compatibilidad"]["es_compatible"] is True
    assert len(data["resultados_compatibilidad"]["incompatibilidades"]) == 0


def test_validar_pc_incompatible():
    """Prueba el endpoint enviando componentes que generen conflictos de reglas."""
    payload = {
        "nombre_configuracion": "PC Incompatible",
        "componentes": [
            {
                "id_componente": 4,
                "nombre": "Intel Core i7",
                "tipo": "Procesador",
                "consumo_watts": 125,
                "precio": 350.0,
                "especificaciones": {"socket": "LGA1700"}
            },
            {
                "id_componente": 5,
                "nombre": "Placa Madre B650",
                "tipo": "Placa Madre",
                "consumo_watts": 30,
                "precio": 150.0,
                "especificaciones": {"socket": "AM5"}  # Socket distinto al CPU
            },
            {
                "id_componente": 6,
                "nombre": "Fuente 100W",
                "tipo": "Fuente de Poder",
                "consumo_watts": 0,
                "precio": 20.0,
                "especificaciones": {"watts": 100}  # Fuente muy chica para 155W
            }
        ]
    }

    response = client.post("/api/v1/pc/validar-compatibilidad", json=payload)

    # El status debe seguir siendo 200 porque la petición es correcta (la lógica de negocio es la que "falla")
    assert response.status_code == 200
    
    data = response.json()
    assert data["resultados_compatibilidad"]["es_compatible"] is False
    # Deben detectarse al menos 2 errores: Socket y Fuente
    assert len(data["resultados_compatibilidad"]["incompatibilidades"]) >= 2


def test_validar_pc_payload_invalido():
    """Prueba que Pydantic rechace peticiones con datos faltantes o mal formados."""
    payload_incompleto = {
        "nombre_configuracion": "PC Rota",
        "componentes": [
            {
                "id_componente": 1,
                "nombre": "Solo tengo nombre y tipo",
                "tipo": "Procesador"
                # Faltan consumo_watts, precio y especificaciones
            }
        ]
    }

    response = client.post("/api/v1/pc/validar-compatibilidad", json=payload_incompleto)

    # FastAPI debe retornar 422 Unprocessable Entity automáticamente
    assert response.status_code == 422
    errores = response.json()["detail"]
    assert any("consumo_watts" in error["loc"] for error in errores)
    assert any("precio" in error["loc"] for error in errores)
