import pytest
from typing import Optional, Dict, Any

from app.domain.modelos import ConfiguracionPC
from app.domain.reglas import ReglaCompatibilidadStrategy
from app.services.compatibilidad_service import ValidadorCompatibilidadService

# --- Clases Mock para aislar el testeo del Servicio ---

class ReglaMockFalla(ReglaCompatibilidadStrategy):
    """Simula una regla que siempre encuentra una incompatibilidad."""
    def __init__(self):
        super().__init__(id_regla=99, nombre="Regla Falsa", codigo="FAIL_MOCK", nivel="ERROR")

    def evaluar(self, configuracion: ConfiguracionPC) -> Optional[Dict[str, Any]]:
        return {
            "resultado": "INCOMPATIBLE",
            "nivel": self.nivel,
            "mensaje": "Esta regla siempre falla para forzar el test."
        }

class ReglaMockPasa(ReglaCompatibilidadStrategy):
    """Simula una regla que siempre valida correctamente la PC."""
    def __init__(self):
        super().__init__(id_regla=100, nombre="Regla Verdadera", codigo="PASS_MOCK", nivel="INFO")

    def evaluar(self, configuracion: ConfiguracionPC) -> Optional[Dict[str, Any]]:
        return None  # Retornar None significa que pasó la validación


# --- Tests Unitarios del Servicio ---

def test_servicio_inicializacion_por_defecto():
    """Verifica que el servicio cargue las 4 reglas base si no se le inyectan dependencias externas."""
    servicio = ValidadorCompatibilidadService()
    
    assert len(servicio.reglas) == 4
    # Comprobamos que instanció las clases hijas reales
    nombres_reglas = [type(r).__name__ for r in servicio.reglas]
    assert "ReglaConsumoFuenteStrategy" in nombres_reglas
    assert "ReglaSocketCpuMotherboardStrategy" in nombres_reglas

def test_servicio_configuracion_compatible():
    """Verifica que el servicio consolide un 'es_compatible = True' si las reglas devuelven None."""
    regla = ReglaMockPasa()
    servicio = ValidadorCompatibilidadService(reglas=[regla])
    config_vacia = ConfiguracionPC()

    resultado = servicio.validar_configuracion(config_vacia)

    assert resultado["es_compatible"] is True
    assert len(resultado["incompatibilidades"]) == 0
    assert len(resultado["detalles"]) == 0

def test_servicio_configuracion_incompatible():
    """Verifica el mapeo de errores cuando una o más reglas fallan."""
    regla_falla = ReglaMockFalla()
    regla_pasa = ReglaMockPasa()
    
    # Inyectamos ambas reglas al servicio
    servicio = ValidadorCompatibilidadService(reglas=[regla_pasa, regla_falla])
    config_vacia = ConfiguracionPC()

    resultado = servicio.validar_configuracion(config_vacia)

    assert resultado["es_compatible"] is False
    assert len(resultado["incompatibilidades"]) == 1
    assert "Esta regla siempre falla" in resultado["incompatibilidades"][0]
    
    # Validamos que se haya mapeado correctamente el detalle
    assert len(resultado["detalles"]) == 1
    assert resultado["detalles"][0]["codigo_regla"] == "FAIL_MOCK"
    assert resultado["detalles"][0]["id_regla"] == 99

def test_servicio_ignora_reglas_inactivas():
    """Verifica el comportamiento de la bandera 'activa'. El servicio debe saltar (continue) la regla."""
    regla_inactiva = ReglaMockFalla()
    regla_inactiva.activa = False  # Apagamos explícitamente la regla que iba a fallar

    servicio = ValidadorCompatibilidadService(reglas=[regla_inactiva])
    config_vacia = ConfiguracionPC()

    resultado = servicio.validar_configuracion(config_vacia)

    # Al ser ignorada la regla fallida, el resultado general debe ser compatible
    assert resultado["es_compatible"] is True
    assert len(resultado["incompatibilidades"]) == 0
