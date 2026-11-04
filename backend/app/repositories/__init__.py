"""Repositorios de acceso a PostgreSQL."""

from app.repositories.componente_repository import ComponenteRepository
from app.repositories.perfil_repository import PerfilRepository
from app.repositories.usuario_repository import UsuarioRepository

__all__ = [
    "ComponenteRepository",
    "PerfilRepository",
    "UsuarioRepository",
]
