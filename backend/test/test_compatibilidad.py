import pytest
from app.domain.modelos import Usuario, Marca, TipoComponente, Componente, ConfiguracionPC
from app.domain.reglas import ReglaConsumoFuenteStrategy, ReglaSocketCpuMotherboardStrategy
from app.services.compatibilidad_service import ValidadorCompatibilidadService

@pytest.fixture
def fixture_base():
    """Fixture de Pytest para preparar datos comunes de prueba."""
    usuario = Usuario(id_usuario=1, nombre="Carlos", apellido="Pérez", email="carlos@mail.com", password_hash="hash123")
    
    # Marcas
    marca_amd = Marca(id_marca=1, nombre="AMD")
    marca_asus = Marca(id_marca=2, nombre="ASUS")
    marca_corsair = Marca(id_marca=3, nombre="Corsair")
    
    # Tipos de componentes
    t_cpu = TipoComponente(id_tipo=1, nombre="Procesador", obligatorio=True)
    t_mother = TipoComponente(id_tipo=2, nombre="Placa Madre", obligatorio=True)
    t_fuente = TipoComponente(id_tipo=3, nombre="Fuente de Poder", obligatorio=True)
    t_gpu = TipoComponente(id_tipo=4, nombre="Placa de Video", obligatorio=False)

    return usuario, marca_amd, marca_asus, marca_corsair, t_cpu, t_mother, t_fuente, t_gpu


def test_regla_consumo_fuente_insuficiente(fixture_base):
    usuario, amd, asus, corsair, t_cpu, t_mother, t_fuente, t_gpu = fixture_base
    
    # Creamos una PC
    config = ConfiguracionPC(id_configuracion=1, usuario=usuario, nombre="PC Gamer Básica")
    
    # Fuente débil de 400W
    fuente = Componente(1, t_fuente, corsair, "CV400", "400W", "Genérica", consumo_watts=0, precio_referencia=60.0, stock=10, especificaciones={"watts": 400})
    # GPU que consume mucho (450W)
    gpu = Componente(2, t_gpu, amd, "RX 7900", "XT", "Poderosa", consumo_watts=450, precio_referencia=800.0, stock=5, especificaciones={})
    
    config.agregar_componente(fuente)
    config.agregar_componente(gpu)
    
    # Instanciamos la regla de consumo
    regla_watts = ReglaConsumoFuenteStrategy(1, "Capacidad Fuente", "Verifica watts", "VAL_WATTS", "ERROR")
    servicio = ValidadorCompatibilidadService(reglas=[regla_watts])
    
    # Ejecutamos la validación
    resultados = servicio.validar_configuracion(config)
    
    # Aserciones (Verificamos que detecte la incompatibilidad de energía)
    assert len(resultados) == 1
    assert resultados[0]["resultado"] == "INCOMPATIBLE"
    assert "supera la capacidad de la fuente" in resultados[0]["mensaje"]


def test_regla_socket_incompatible(fixture_base):
    usuario, amd, asus, corsair, t_cpu, t_mother, t_fuente, t_gpu = fixture_base
    
    config = ConfiguracionPC(id_configuracion=2, usuario=usuario, nombre="PC Errónea")
    
    # CPU con socket AM5
    cpu = Componente(1, t_cpu, amd, "Ryzen 5 7600", "AM5", "Buen CPU", consumo_watts=65, precio_referencia=250.0, stock=5, especificaciones={"socket": "AM5"})
    # Placa madre con socket LGA1700 (Intel)
    mother = Componente(2, t_mother, asus, "Prime H610M", "LGA1700", "Placa Intel", consumo_watts=20, precio_referencia=120.0, stock=5, especificaciones={"socket": "LGA1700"})
    
    config.agregar_componente(cpu)
    config.agregar_componente(mother)
    
    # Instanciamos la regla de socket
    regla_socket = ReglaSocketCpuMotherboardStrategy(2, "Socket CPU/Mother", "Verifica sockets", "VAL_SOCKET", "ERROR")
    servicio = ValidadorCompatibilidadService(reglas=[regla_socket])
    
    resultados = servicio.validar_configuracion(config)
    
    assert len(resultados) == 1
    assert resultados[0]["resultado"] == "INCOMPATIBLE"
    assert "Incompatibilidad de socket" in resultados[0]["mensaje"]


def test_configuracion_exitosa_compatible(fixture_base):
    usuario, amd, asus, corsair, t_cpu, t_mother, t_fuente, t_gpu = fixture_base
    
    config = ConfiguracionPC(id_configuracion=3, usuario=usuario, nombre="PC Perfecta")
    
    # Fuente robusta de 750W
    fuente = Componente(1, t_fuente, corsair, "RM750x", "750W", "Excelente", consumo_watts=0, precio_referencia=150.0, stock=10, especificaciones={"watts": 750})
    # CPU y Mother con el mismo socket AM5
    cpu = Componente(2, t_cpu, amd, "Ryzen 7 7700X", "AM5", "Gamer", consumo_watts=105, precio_referencia=350.0, stock=5, especificaciones={"socket": "AM5"})
    mother = Componente(3, t_mother, asus, "TUF Gaming B650", "AM5", "Robusta", consumo_watts=30, precio_referencia=200.0, stock=5, especificaciones={"socket": "AM5"})
    
    config.agregar_componente(fuente)
    config.agregar_componente(cpu)
    config.agregar_componente(mother)
    
    # Inyectamos ambas reglas
    regla_watts = ReglaConsumoFuenteStrategy(1, "Capacidad Fuente", "Verifica watts", "VAL_WATTS", "ERROR")
    regla_socket = ReglaSocketCpuMotherboardStrategy(2, "Socket CPU/Mother", "Verifica sockets", "VAL_SOCKET", "ERROR")
    
    servicio = ValidadorCompatibilidadService(reglas=[regla_watts, regla_socket])
    resultados = servicio.validar_configuracion(config)
    
    # Debe pasar exitosamente sin errores
    assert len(resultados) == 1
    assert resultados[0]["resultado"] == "COMPATIBLE"
    assert "compatibles entre sí" in resultados[0]["mensaje"]