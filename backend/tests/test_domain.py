import pytest
from app.domain.modelos import ConfiguracionPC, Componente, TipoComponente, ConfiguracionComponente
from app.domain.reglas import (
    ReglaConsumoFuenteStrategy,
    ReglaSocketCpuMotherboardStrategy,
)

# --- Fixtures auxiliares ---
@pytest.fixture
def tipo_cpu():
    return TipoComponente(nombre="Procesador")

@pytest.fixture
def tipo_fuente():
    return TipoComponente(nombre="Fuente de poder")

@pytest.fixture
def tipo_mother():
    return TipoComponente(nombre="Placa madre")


# --- Tests para Modelos (Lógica interna) ---
def test_consumo_total_watts_calculo_correcto():
    """Verifica la suma del consumo teniendo en cuenta las cantidades."""
    cpu = Componente(nombre="CPU Ficticia", consumo_watts=65)
    gpu = Componente(nombre="GPU Ficticia", consumo_watts=200)
    
    config = ConfiguracionPC()
    config.componentes_agregados = [
        ConfiguracionComponente(componente=cpu, cantidad=1), # 65W
        ConfiguracionComponente(componente=gpu, cantidad=2)  # 400W
    ]
    
    assert config.consumo_total_watts == 465

def test_consumo_total_watts_lista_vacia():
    """Verifica que retorne 0 si no hay componentes."""
    config = ConfiguracionPC()
    config.componentes_agregados = []
    
    assert config.consumo_total_watts == 0


# --- Tests Unitarios Aislados para Reglas ---
def test_regla_consumo_fuente_sin_fuente_asignada(tipo_cpu):
    """Debe fallar si hay consumo pero no hay una PSU en la configuración."""
    cpu = Componente(nombre="CPU", tipo=tipo_cpu, consumo_watts=100)
    config = ConfiguracionPC(
        componentes_agregados=[ConfiguracionComponente(componente=cpu, cantidad=1)]
    )
    
    regla = ReglaConsumoFuenteStrategy()
    resultado = regla.evaluar(config)
    
    assert resultado is not None
    assert resultado["resultado"] == "INCOMPATIBLE"
    assert "Falta agregar una fuente de poder" in resultado["mensaje"]

def test_regla_consumo_fuente_potencia_insuficiente(tipo_cpu, tipo_fuente):
    """Debe fallar si los componentes consumen más de lo que la fuente provee."""
    cpu = Componente(nombre="CPU", tipo=tipo_cpu, consumo_watts=300)
    fuente = Componente(nombre="PSU", tipo=tipo_fuente, especificaciones={"watts": 250})
    
    config = ConfiguracionPC(
        componentes_agregados=[
            ConfiguracionComponente(componente=cpu, cantidad=1),
            ConfiguracionComponente(componente=fuente, cantidad=1)
        ]
    )
    
    regla = ReglaConsumoFuenteStrategy()
    resultado = regla.evaluar(config)
    
    assert resultado is not None
    assert resultado["resultado"] == "INCOMPATIBLE"
    assert "supera la capacidad de la fuente seleccionada" in resultado["mensaje"]

def test_regla_socket_cpu_motherboard_incompatible(tipo_cpu, tipo_mother):
    """Debe detectar cuando los sockets no coinciden exactamente."""
    cpu = Componente(nombre="CPU Ryzen", tipo=tipo_cpu, especificaciones={"socket": "AM5"})
    mother = Componente(nombre="Mother Intel", tipo=tipo_mother, especificaciones={"socket": "LGA1700"})
    
    config = ConfiguracionPC(
        componentes_agregados=[
            ConfiguracionComponente(componente=cpu, cantidad=1),
            ConfiguracionComponente(componente=mother, cantidad=1)
        ]
    )
    
    regla = ReglaSocketCpuMotherboardStrategy()
    resultado = regla.evaluar(config)
    
    assert resultado is not None
    assert resultado["resultado"] == "INCOMPATIBLE"
    assert "Incompatibilidad de socket" in resultado["mensaje"]

def test_regla_socket_cpu_motherboard_compatible(tipo_cpu, tipo_mother):
    """Debe retornar None (sin errores) cuando los sockets son iguales."""
    cpu = Componente(nombre="CPU Ryzen", tipo=tipo_cpu, especificaciones={"socket": "AM5"})
    mother = Componente(nombre="Mother AMD", tipo=tipo_mother, especificaciones={"socket": "AM5"})
    
    config = ConfiguracionPC(
        componentes_agregados=[
            ConfiguracionComponente(componente=cpu, cantidad=1),
            ConfiguracionComponente(componente=mother, cantidad=1)
        ]
    )
    
    regla = ReglaSocketCpuMotherboardStrategy()
    resultado = regla.evaluar(config)
    
    assert resultado is None
