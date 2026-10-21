"""
Repositorio de perfiles de uso.

Centraliza las consultas relacionadas con perfiles funcionales,
categorías requeridas y componentes recomendados.
"""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.conexion import SessionLocal


class PerfilRepository:
    """Repositorio de acceso a perfiles almacenados en PostgreSQL."""

    def obtener_todos(self):
        """Obtiene todos los perfiles activos en orden visual."""

        consulta = text("""
            SELECT
                id_perfil,
                codigo,
                nombre,
                descripcion,
                texto_destacado,
                orden_visual
            FROM perfiles_uso
            WHERE activo = TRUE
            ORDER BY orden_visual, nombre
        """)

        return self._obtener_varios(
            consulta,
            {},
            "No se pudieron obtener los perfiles.",
        )

    def obtener_por_id(self, id_perfil: int):
        """Obtiene un perfil activo mediante su identificador."""

        consulta = text("""
            SELECT
                id_perfil,
                codigo,
                nombre,
                descripcion,
                texto_destacado,
                orden_visual
            FROM perfiles_uso
            WHERE id_perfil = :id_perfil
              AND activo = TRUE
        """)

        return self._obtener_uno(
            consulta,
            {"id_perfil": id_perfil},
            f"No se pudo obtener el perfil {id_perfil}.",
        )

    def obtener_por_codigo(self, codigo: str):
        """Obtiene un perfil activo mediante su código."""

        consulta = text("""
            SELECT
                id_perfil,
                codigo,
                nombre,
                descripcion,
                texto_destacado,
                orden_visual
            FROM perfiles_uso
            WHERE codigo = :codigo
              AND activo = TRUE
        """)

        return self._obtener_uno(
            consulta,
            {"codigo": codigo},
            f"No se pudo obtener el perfil con código {codigo}.",
        )

    def obtener_categorias(self, id_perfil: int):
        """Obtiene las categorías requeridas por un perfil."""

        consulta = text("""
            SELECT
                t.id_tipo,
                t.nombre,
                t.descripcion,
                ptc.obligatorio,
                ptc.prioridad,
                ptc.cantidad_sugerida
            FROM perfil_tipos_componente ptc
            INNER JOIN tipos_componente t
                ON t.id_tipo = ptc.id_tipo
            WHERE ptc.id_perfil = :id_perfil
            ORDER BY
                ptc.prioridad DESC,
                ptc.obligatorio DESC,
                t.nombre
        """)

        return self._obtener_varios(
            consulta,
            {"id_perfil": id_perfil},
            f"No se pudieron obtener las categorías del perfil {id_perfil}.",
        )

    def obtener_componentes(self, id_perfil: int):
        """Obtiene los componentes asociados a un perfil."""

        consulta = text("""
            SELECT
                c.id_componente,
                c.id_tipo,
                c.nombre,
                c.modelo,
                c.descripcion,
                c.consumo_watts,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                t.nombre AS categoria,
                m.nombre AS marca,
                pc.afinidad,
                pc.recomendado,
                pc.observacion
            FROM perfil_componentes pc
            INNER JOIN componentes c
                ON c.id_componente = pc.id_componente
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE pc.id_perfil = :id_perfil
              AND c.activo = TRUE
            ORDER BY
                pc.recomendado DESC,
                pc.afinidad DESC,
                t.nombre,
                c.precio_referencia
        """)

        return self._obtener_varios(
            consulta,
            {"id_perfil": id_perfil},
            f"No se pudieron obtener los componentes del perfil {id_perfil}.",
        )

    def obtener_componentes_recomendados(self, id_perfil: int):
        """Obtiene solamente los componentes recomendados para un perfil."""

        consulta = text("""
            SELECT
                c.id_componente,
                c.id_tipo,
                c.nombre,
                c.modelo,
                c.descripcion,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                t.nombre AS categoria,
                m.nombre AS marca,
                pc.afinidad,
                pc.observacion
            FROM perfil_componentes pc
            INNER JOIN componentes c
                ON c.id_componente = pc.id_componente
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE pc.id_perfil = :id_perfil
              AND pc.recomendado = TRUE
              AND c.activo = TRUE
            ORDER BY
                pc.afinidad DESC,
                t.nombre,
                c.precio_referencia
        """)

        return self._obtener_varios(
            consulta,
            {"id_perfil": id_perfil},
            (
                "No se pudieron obtener los componentes recomendados "
                f"del perfil {id_perfil}."
            ),
        )

    def _obtener_varios(self, consulta, parametros, mensaje_error):
        """Ejecuta una consulta y devuelve las filas como diccionarios."""

        try:
            with SessionLocal() as db:
                resultado = db.execute(consulta, parametros)
                return [dict(fila) for fila in resultado.mappings().all()]

        except SQLAlchemyError as error:
            raise RuntimeError(mensaje_error) from error

    def _obtener_uno(self, consulta, parametros, mensaje_error):
        """Ejecuta una consulta y devuelve una fila o None."""

        try:
            with SessionLocal() as db:
                resultado = db.execute(consulta, parametros)
                fila = resultado.mappings().first()

                return dict(fila) if fila is not None else None

        except SQLAlchemyError as error:
            raise RuntimeError(mensaje_error) from error
