import pytest
import os
import importlib
from unittest.mock import patch, MagicMock

# Importamos el módulo de conexión
from app.database import conexion

def test_conexion_faltan_variables():
    """Verifica que el módulo lance RuntimeError si faltan credenciales obligatorias."""
    
    # patch.dict limpia temporalmente las variables de entorno para este test
    with patch.dict(os.environ, {}, clear=True):
        # Aseguramos que DB_USER y DB_PASSWORD devuelvan None
        os.environ.pop("DB_USER", None)
        os.environ.pop("DB_PASSWORD", None)
        
        with pytest.raises(RuntimeError) as exc_info:
            # Recargamos el módulo para forzar a que el código global vuelva a ejecutarse
            importlib.reload(conexion)
        
        # Validamos que el mensaje de error sea el correcto
        assert "Faltan variables de entorno requeridas" in str(exc_info.value)
        assert "DB_USER" in str(exc_info.value)
        assert "DB_PASSWORD" in str(exc_info.value)
        
    # IMPORTANTE: Volvemos a recargar el módulo ya sin el "patch" para que recupere
    # tu .env real y no rompa los demás tests que se ejecuten después de este.
    importlib.reload(conexion)


@patch("app.database.conexion.SessionLocal")
def test_get_db_yield_y_cierre(mock_session_local):
    """Verifica que el generador entregue la sesión y la cierre al terminar."""
    
    # Simulamos el objeto db (la sesión de SQLAlchemy)
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    # Invocamos al generador
    generador = conexion.get_db()
    
    # 1. Simulamos el momento en que FastAPI pide la dependencia (yield)
    db_generada = next(generador)
    
    # Verificamos que la sesión entregada sea la que creamos
    assert db_generada == mock_db
    # Verificamos que todavía NO se haya cerrado
    mock_db.close.assert_not_called()

    # 2. Simulamos el momento en que FastAPI termina el request y continúa la función
    with pytest.raises(StopIteration):
        next(generador)
        
    # Verificamos que el bloque 'finally' ejecutó db.close() exitosamente
    mock_db.close.assert_called_once()
