import importlib
from unittest.mock import MagicMock, patch

import pytest

# Importamos el módulo de conexión
from app.database import conexion


def test_conexion_faltan_variables():
    """Verifica que el módulo lance RuntimeError si faltan credenciales obligatorias."""
    
    # Interceptamos directamente la función os.getenv y load_dotenv dentro de tu archivo
    with patch("app.database.conexion.os.getenv") as mock_getenv, \
         patch("app.database.conexion.load_dotenv"):
         
        # Creamos un comportamiento falso: si pide USER o PASSWORD, forzamos que reciba None.
        # Para cualquier otra variable (como DB_HOST o PORT), le devolvemos su valor por defecto.
        def getenv_falso(key, default=None):
            if key in ["DB_USER", "DB_PASSWORD"]:
                return None
            return default
            
        mock_getenv.side_effect = getenv_falso
        
        # Ahora sí, al recargar el archivo, os.getenv devolverá None y debe explotar
        with pytest.raises(RuntimeError) as exc_info:
            importlib.reload(conexion)
        
        # Validamos que el mensaje de error sea el esperado
        assert "Faltan variables de entorno requeridas" in str(exc_info.value)
        assert "DB_USER" in str(exc_info.value)
        assert "DB_PASSWORD" in str(exc_info.value)

    # Al salir del bloque 'with', la trampa desaparece y os.getenv vuelve a la normalidad.
    # Recargamos el módulo una última vez para que recupere tu .env real.
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
