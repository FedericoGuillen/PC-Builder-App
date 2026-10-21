
"""
Pruebas de integración de los repositorios.

Requieren una base PostgreSQL creada y con datos cargados.
"""

from app.repositories.componente_repository import ComponenteRepository
from app.repositories.perfil_repository import PerfilRepository


def test_obtener_componentes():
    repository = ComponenteRepository()

    componentes = repository.obtener_todos()

    assert isinstance(componentes, list)
    assert len(componentes) > 0


def test_obtener_categorias():
    repository = ComponenteRepository()

    categorias = repository.obtener_categorias()

    assert isinstance(categorias, list)
    assert len(categorias) > 0


def test_obtener_componente_por_id():
    repository = ComponenteRepository()

    componente = repository.obtener_por_id(1)

    assert componente is not None
    assert componente["id_componente"] == 1


def test_obtener_componente_inexistente():
    repository = ComponenteRepository()

    componente = repository.obtener_por_id(999999999)

    assert componente is None


def test_obtener_placas_madre_por_socket():
    repository = ComponenteRepository()

    placas = repository.obtener_placas_madre_por_socket("AM5")

    assert isinstance(placas, list)


def test_obtener_memorias_por_tipo():
    repository = ComponenteRepository()

    memorias = repository.obtener_memorias_por_tipo("DDR5")

    assert isinstance(memorias, list)


def test_obtener_gabinetes_por_factor_forma():
    repository = ComponenteRepository()

    gabinetes = repository.obtener_gabinetes_por_factor_forma("ATX")

    assert isinstance(gabinetes, list)


def test_obtener_fuentes_por_potencia_minima():
    repository = ComponenteRepository()

    fuentes = repository.obtener_fuentes_por_potencia_minima(750)

    assert isinstance(fuentes, list)

    for fuente in fuentes:
        assert fuente["potencia_w"] >= 750


def test_obtener_perfiles():
    repository = PerfilRepository()

    perfiles = repository.obtener_todos()

    assert isinstance(perfiles, list)
    assert len(perfiles) > 0


def test_obtener_componentes_por_perfil():
    repository = PerfilRepository()
    perfiles = repository.obtener_todos()

    assert len(perfiles) > 0

    componentes = repository.obtener_componentes(
        perfiles[0]["id_perfil"]
    )

    assert isinstance(componentes, list)
