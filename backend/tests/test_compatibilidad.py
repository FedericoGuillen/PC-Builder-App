import pytest
from app.domain.modelos import ConfiguracionPC, Componente, TipoComponente
from app.services.compatibilidad_service import ValidadorCompatibilidadService

@pytest.fixture
def validador():
    return ValidadorCompatibilidadService()

# Tipos de componentes de prueba simulados
tipo_cpu = TipoComponente(nombre="Procesador")
tipo_mother = TipoComponente(nombre="Placa Madre")
tipo_ram = TipoComponente(nombre="Memoria RAM")
tipo_gab = TipoComponente(nombre="Gabinete")
tipo_fuente = TipoComponente(nombre="Fuente de Poder")

def test_configuracion_compatible(validador):
    """Criterio 10: Verifica que componentes compatibles pasen todas las reglas sin errores."""
    cpu = Componente(nombre="Ryzen 5 7600", tipo=tipo_cpu, consumo_watts=65, especificaciones={"socket": "AM5"})
    mother = Componente(nombre="B650 Motherboard", tipo=tipo_mother, consumo_watts=30, especificaciones={"socket": "AM5", "tipo_ram": "DDR5", "factor_forma": "ATX"})
    ram = Componente(nombre="RAM 16GB DDR5", tipo=tipo_ram, consumo_watts=5, especificaciones={"tipo_ram": "DDR5"})
    gabinete = Componente(nombre="Gabinete ATX", tipo=tipo_gab, consumo_watts=0, especificaciones={"factores_forma_soportados": ["ATX", "Micro-ATX"]})
    fuente = Componente(nombre="Fuente 600W", tipo=tipo_fuente, consumo_watts=0, especificaciones={"watts": 600})

    # Instanciamos la PC y usamos el método oficial de tu dominio para agregar piezas
    config = ConfiguracionPC(nombre="PC Test Compatible")
    config.agregar_componente(cpu)
    config.agregar_componente(mother)
    config.agregar_componente(ram)
    config.agregar_componente(gabinete)
    config.agregar_componente(fuente)

    resultado = validador.validar_configuracion(config)

    assert resultado["es_compatible"] is True
    assert len(resultado["incompatibilidades"]) == 0


def test_configuracion_incompatible(validador):
    """Criterio 11: Verifica que componentes incompatibles (socket distinto y fuente chica) devuelvan errores."""
    cpu = Componente(nombre="Intel Core i5", tipo=tipo_cpu, consumo_watts=150, especificaciones={"socket": "LGA1700"})
    mother = Componente(nombre="B650 Motherboard", tipo=tipo_mother, consumo_watts=30, especificaciones={"socket": "AM5", "tipo_ram": "DDR4", "factor_forma": "ATX"})
    fuente = Componente(nombre="Fuente 100W", tipo=tipo_fuente, consumo_watts=0, especificaciones={"watts": 100})

    config = ConfiguracionPC(nombre="PC Test Incompatible")
    config.agregar_componente(cpu)
    config.agregar_componente(mother)
    config.agregar_componente(fuente)

    resultado = validador.validar_configuracion(config)

    assert resultado["es_compatible"] is False
    # Validamos que se detecten múltiples errores simultáneos
    assert len(resultado["incompatibilidades"]) > 0
