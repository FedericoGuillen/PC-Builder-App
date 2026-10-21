"""Repositorios de acceso a PostgreSQL."""

from app.repositories.componente_repository import ComponenteRepository
from app.repositories.perfil_repository import PerfilRepository

__all__ = [
    "ComponenteRepository",
    "PerfilRepository",
]
