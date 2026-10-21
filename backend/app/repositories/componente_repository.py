"""
Repositorio de componentes.

Centraliza las consultas de componentes y categorías realizadas
sobre PostgreSQL mediante SQLAlchemy.
"""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.conexion import SessionLocal


class ComponenteRepository:
    """Repositorio de acceso a componentes y tipos de componente."""

    def obtener_todos(self):
        """Obtiene todos los componentes activos."""

        consulta = text("""
            SELECT
                c.id_componente,
                c.id_tipo,
                c.id_marca,
                c.nombre,
                c.modelo,
                c.descripcion,
                c.consumo_watts,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                c.imagen_url,
                c.activo,
                t.nombre AS categoria,
                m.nombre AS marca
            FROM componentes c
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE c.activo = TRUE
            ORDER BY t.nombre, c.nombre, c.modelo
        """)

        return self._obtener_varios(
            consulta,
            {},
            "No se pudieron obtener los componentes.",
        )

    def obtener_categorias(self):
        """Obtiene todas las categorías de componentes."""

        consulta = text("""
            SELECT
                id_tipo,
                nombre,
                descripcion,
                cantidad_maxima_sugerida,
                obligatorio
            FROM tipos_componente
            ORDER BY nombre
        """)

        return self._obtener_varios(
            consulta,
            {},
            "No se pudieron obtener las categorías.",
        )

    def obtener_por_categoria(self, id_tipo: int):
        """Obtiene los componentes activos de una categoría."""

        consulta = text("""
            SELECT
                c.id_componente,
                c.id_tipo,
                c.id_marca,
                c.nombre,
                c.modelo,
                c.descripcion,
                c.consumo_watts,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                c.imagen_url,
                t.nombre AS categoria,
                m.nombre AS marca
            FROM componentes c
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE c.id_tipo = :id_tipo
              AND c.activo = TRUE
            ORDER BY c.nombre, c.modelo
        """)

        return self._obtener_varios(
            consulta,
            {"id_tipo": id_tipo},
            f"No se pudieron obtener los componentes del tipo {id_tipo}.",
        )

    def obtener_por_id(self, id_componente: int):
        """Obtiene un componente activo mediante su identificador."""

        consulta = text("""
            SELECT
                c.id_componente,
                c.id_tipo,
                c.id_marca,
                c.nombre,
                c.modelo,
                c.descripcion,
                c.consumo_watts,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                c.imagen_url,
                c.activo,
                c.fecha_creacion,
                t.nombre AS categoria,
                m.nombre AS marca
            FROM componentes c
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE c.id_componente = :id_componente
              AND c.activo = TRUE
        """)

        return self._obtener_uno(
            consulta,
            {"id_componente": id_componente},
            f"No se pudo obtener el componente {id_componente}.",
        )

    def obtener_por_perfil(self, id_perfil: int):
        """
        Obtiene los componentes asociados a un perfil.

        Los resultados se ordenan primero por recomendación y luego
        por afinidad, desde el valor más alto al más bajo.
        """

        consulta = text("""
            SELECT
                c.id_componente,
                c.id_tipo,
                c.id_marca,
                c.nombre,
                c.modelo,
                c.descripcion,
                c.consumo_watts,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                c.imagen_url,
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
                c.nombre
        """)

        return self._obtener_varios(
            consulta,
            {"id_perfil": id_perfil},
            f"No se pudieron obtener los componentes del perfil {id_perfil}.",
        )

    def obtener_placas_madre_por_socket(self, socket: str):
        """Obtiene motherboards compatibles con un socket."""

        consulta = text("""
            SELECT
                c.id_componente,
                c.nombre,
                c.modelo,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                m.nombre AS marca
            FROM componentes c
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE t.nombre = 'MOTHERBOARD'
              AND c.especificaciones ->> 'socket' = :socket
              AND c.activo = TRUE
            ORDER BY c.precio_referencia, c.nombre
        """)

        return self._obtener_varios(
            consulta,
            {"socket": socket},
            f"No se pudieron obtener placas madre para el socket {socket}.",
        )

    def obtener_memorias_por_tipo(self, tipo_memoria: str):
        """Obtiene memorias RAM según el tipo indicado, por ejemplo DDR5."""

        consulta = text("""
            SELECT
                c.id_componente,
                c.nombre,
                c.modelo,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                m.nombre AS marca
            FROM componentes c
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE t.nombre = 'RAM'
              AND c.especificaciones ->> 'tipo' = :tipo_memoria
              AND c.activo = TRUE
            ORDER BY
                (c.especificaciones ->> 'capacidad_gb')::INTEGER,
                (c.especificaciones ->> 'velocidad_mhz')::INTEGER,
                c.nombre
        """)

        return self._obtener_varios(
            consulta,
            {"tipo_memoria": tipo_memoria},
            f"No se pudieron obtener memorias de tipo {tipo_memoria}.",
        )

    def obtener_gabinetes_por_factor_forma(self, factor_forma: str):
        """
        Obtiene gabinetes compatibles con un factor de forma.

        El campo form_factor es un arreglo JSON, por ejemplo:
        ["ATX", "Micro-ATX", "Mini-ITX"].
        """

        consulta = text("""
            SELECT
                c.id_componente,
                c.nombre,
                c.modelo,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                m.nombre AS marca
            FROM componentes c
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE t.nombre = 'CASE'
              AND EXISTS (
                  SELECT 1
                  FROM jsonb_array_elements_text(
                      c.especificaciones -> 'form_factor'
                  ) AS formato(valor)
                  WHERE formato.valor = :factor_forma
              )
              AND c.activo = TRUE
            ORDER BY c.precio_referencia, c.nombre
        """)

        return self._obtener_varios(
            consulta,
            {"factor_forma": factor_forma},
            (
                "No se pudieron obtener gabinetes para el factor "
                f"de forma {factor_forma}."
            ),
        )

 def obtener_fuentes_por_potencia_minima(self, potencia_minima: int):
        """Obtiene fuentes con potencia igual o superior a la solicitada."""

        consulta = text("""
            SELECT
                c.id_componente,
                c.nombre,
                c.modelo,
                c.precio_referencia,
                c.stock,
                c.especificaciones,
                m.nombre AS marca,
                (c.especificaciones ->> 'potencia_w')::INTEGER AS potencia_w
            FROM componentes c
            INNER JOIN tipos_componente t
                ON t.id_tipo = c.id_tipo
            INNER JOIN marcas m
                ON m.id_marca = c.id_marca
            WHERE t.nombre = 'PSU'
              AND (c.especificaciones ->> 'potencia_w')::INTEGER >= :potencia_minima
              AND c.activo = TRUE
            ORDER BY
                (c.especificaciones ->> 'potencia_w')::INTEGER,
                c.precio_referencia,
                c.nombre
        """)

        return self._obtener_varios(
            consulta,
            {"potencia_minima": potencia_minima},
            f"No se pudieron obtener fuentes con potencia mínima {potencia_minima}W.",
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
