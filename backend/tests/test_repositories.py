import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.componente_repository import ComponenteRepository
from app.repositories.perfil_repository import PerfilRepository

# ====================================================================
# Tests para ComponenteRepository
# ====================================================================

@patch("app.repositories.componente_repository.SessionLocal")
def test_obtener_todos_componentes(mock_session_local):
    """Verifica que el repositorio ejecute la consulta y mapee múltiples resultados."""
    # 1. Configuramos el mock para simular el bloque 'with SessionLocal() as db:'
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db
    
    # 2. Simulamos el resultado de SQLAlchemy mappings().all()
    mock_resultado = MagicMock()
    mock_resultado.mappings().all.return_value = [
        {"id_componente": 1, "nombre": "Ryzen 5 7600", "marca": "AMD"},
        {"id_componente": 2, "nombre": "Core i5 14600K", "marca": "Intel"}
    ]
    mock_db.execute.return_value = mock_resultado

    # 3. Ejecutamos el método
    repo = ComponenteRepository()
    componentes = repo.obtener_todos()

    # 4. Validaciones
    assert len(componentes) == 2
    assert componentes[0]["nombre"] == "Ryzen 5 7600"
    mock_db.execute.assert_called_once() # Verifica que se llamó a la base de datos


@patch("app.repositories.componente_repository.SessionLocal")
def test_obtener_componente_por_id(mock_session_local):
    """Verifica el comportamiento al buscar un registro único."""
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db
    
    mock_resultado = MagicMock()
    # Simulamos mappings().first()
    mock_resultado.mappings().first.return_value = {"id_componente": 10, "nombre": "RTX 4060"}
    mock_db.execute.return_value = mock_resultado

    repo = ComponenteRepository()
    componente = repo.obtener_por_id(10)

    assert componente is not None
    assert componente["nombre"] == "RTX 4060"
    
    # Verificamos que el parámetro se haya inyectado correctamente en la consulta
    args, kwargs = mock_db.execute.call_args
    assert kwargs == {"id_componente": 10}


@patch("app.repositories.componente_repository.SessionLocal")
def test_manejo_errores_base_datos_componentes(mock_session_local):
    """Verifica que un fallo de conexión a BD levante un RuntimeError personalizado."""
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db
    
    # Forzamos un error nativo de SQLAlchemy al intentar ejecutar la consulta
    mock_db.execute.side_effect = SQLAlchemyError("Error de conexión a PostgreSQL")

    repo = ComponenteRepository()

    # Validamos que nuestra capa capture el error y levante el RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        repo.obtener_todos()

    assert "No se pudieron obtener los componentes." in str(exc_info.value)


# ====================================================================
# Tests para PerfilRepository
# ====================================================================

@patch("app.repositories.perfil_repository.SessionLocal")
def test_obtener_perfil_por_codigo(mock_session_local):
    """Verifica la obtención de un perfil por su código de texto."""
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db
    
    mock_resultado = MagicMock()
    mock_resultado.mappings().first.return_value = {
        "id_perfil": 1, 
        "codigo": "GAMING_STREAMING", 
        "nombre": "Gaming & Streaming"
    }
    mock_db.execute.return_value = mock_resultado

    repo = PerfilRepository()
    perfil = repo.obtener_por_codigo("GAMING_STREAMING")

    assert perfil is not None
    assert perfil["codigo"] == "GAMING_STREAMING"
    assert "nombre" in perfil


@patch("app.repositories.perfil_repository.SessionLocal")
def test_obtener_perfil_inexistente(mock_session_local):
    """Verifica que devuelva None si no encuentra el perfil."""
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db
    
    mock_resultado = MagicMock()
    # Si la base de datos no encuentra nada, first() devuelve None
    mock_resultado.mappings().first.return_value = None
    mock_db.execute.return_value = mock_resultado

    repo = PerfilRepository()
    perfil = repo.obtener_por_codigo("NO_EXISTE")

    assert perfil is None
