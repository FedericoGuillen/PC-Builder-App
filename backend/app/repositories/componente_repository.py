
"""
Repositorio de consultas de componentes y tipos de componente.

Este módulo centraliza el acceso a PostgreSQL mediante SQLAlchemy.
Las consultas no deben colocarse en main.py ni en la interfaz gráfica.
"""

from sqlalchemy import Integer, cast, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.conexion import SessionLocal
from app.domain.modelos import Componente, TipoComponente


class ComponenteRepository:
    """Repositorio para consultar componentes almacenados en PostgreSQL."""

    def obtener_todos(self):
        """Obtiene todos los componentes."""

        try:
            with SessionLocal() as db:
                consulta = (
                    select(Componente)
                    .order_by(Componente.id_componente)
                )

                return list(db.scalars(consulta).all())

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron obtener los componentes."
            ) from error

    def obtener_categorias(self):
        """
        Obtiene todos los tipos de componente.

        En el modelo actual, TipoComponente representa las categorías
        disponibles, como procesador, memoria, placa madre o gabinete.
        """

        try:
            with SessionLocal() as db:
                consulta = (
                    select(TipoComponente)
                    .order_by(TipoComponente.nombre)
                )

                return list(db.scalars(consulta).all())

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron obtener las categorías."
            ) from error

    def obtener_por_categoria(self, id_tipo: int):
        """Obtiene los componentes correspondientes a un tipo."""

        try:
            with SessionLocal() as db:
                consulta = (
                    select(Componente)
                    .where(Componente.id_tipo == id_tipo)
                    .order_by(Componente.nombre)
                )

                return list(db.scalars(consulta).all())

        except SQLAlchemyError as error:
            raise RuntimeError(
                f"No se pudieron obtener los componentes del tipo {id_tipo}."
            ) from error

    def obtener_por_id(self, id_componente: int):
        """Obtiene un componente mediante su identificador."""

        try:
            with SessionLocal() as db:
                return db.get(Componente, id_componente)

        except SQLAlchemyError as error:
            raise RuntimeError(
                f"No se pudo obtener el componente {id_componente}."
            ) from error

    def obtener_placas_madre_por_socket(self, socket: str):
        """
        Obtiene placas madre que tengan el socket solicitado.

        El socket se consulta dentro del campo JSON especificaciones.
        """

        try:
            with SessionLocal() as db:
                consulta = (
                    select(Componente)
                    .join(
                        TipoComponente,
                        Componente.id_tipo == TipoComponente.id_tipo,
                    )
                    .where(
                        TipoComponente.nombre.ilike("%placa%"),
                        Componente.especificaciones["socket"].astext == socket,
                    )
                    .order_by(Componente.nombre)
                )

                return list(db.scalars(consulta).all())

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron obtener las placas madre por socket."
            ) from error

    def obtener_memorias_por_tipo(self, tipo_memoria: str):
        """
        Obtiene memorias RAM según el tipo indicado.

        Ejemplos de tipo de memoria: DDR4 o DDR5.
        """

        try:
            with SessionLocal() as db:
                consulta = (
                    select(Componente)
                    .join(
                        TipoComponente,
                        Componente.id_tipo == TipoComponente.id_tipo,
                    )
                    .where(
                        TipoComponente.nombre.ilike("%memoria%"),
                        Componente.especificaciones[
                            "tipo_memoria"
                        ].astext == tipo_memoria,
                    )
                    .order_by(Componente.nombre)
                )

                return list(db.scalars(consulta).all())

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron obtener las memorias por tipo."
            ) from error

    def obtener_gabinetes_por_factor_forma(self, factor_forma: str):
        """Obtiene gabinetes según su factor de forma."""

        try:
            with SessionLocal() as db:
                consulta = (
                    select(Componente)
                    .join(
                        TipoComponente,
                        Componente.id_tipo == TipoComponente.id_tipo,
                    )
                    .where(
                        TipoComponente.nombre.ilike("%gabinete%"),
                        Componente.especificaciones[
                            "factor_forma"
                        ].astext == factor_forma,
                    )
                    .order_by(Componente.nombre)
                )

                return list(db.scalars(consulta).all())

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron obtener los gabinetes por factor de forma."
            ) from error

    def obtener_fuentes_por_potencia_minima(self, potencia_minima: int):
        """Obtiene fuentes con una potencia igual o superior a la indicada."""

        try:
            with SessionLocal() as db:
                consulta = (
                    select(Componente)
                    .join(
                        TipoComponente,
                        Componente.id_tipo == TipoComponente.id_tipo,
                    )
                    .where(
                        TipoComponente.nombre.ilike("%fuente%"),
                        cast(
                            Componente.especificaciones["potencia"].astext,
                            Integer,
                        ) >= potencia_minima,
                    )
                    .order_by(
                        cast(
                            Componente.especificaciones["potencia"].astext,
                            Integer,
                        )
                    )
                )

                return list(db.scalars(consulta).all())

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron obtener las fuentes por potencia mínima."
            ) from error
