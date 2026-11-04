"""
Repositorio de usuarios.

Centraliza las consultas y el alta de usuarios sobre PostgreSQL
mediante SQLAlchemy.
"""

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database.conexion import SessionLocal


# Columnas públicas del usuario (sin exponer el hash de la contraseña).
_COLUMNAS_USUARIO = """
    id_usuario,
    nombre,
    apellido,
    email,
    fecha_registro,
    activo
"""


class UsuarioRepository:
    """Repositorio de acceso a la tabla usuarios."""

    def obtener_por_email(self, email: str):
        """Obtiene un usuario (incluido su hash) mediante su email."""

        consulta = text("""
            SELECT
                id_usuario,
                nombre,
                apellido,
                email,
                password_hash,
                fecha_registro,
                activo
            FROM usuarios
            WHERE LOWER(email) = LOWER(:email)
            LIMIT 1
        """)

        return self._obtener_uno(
            consulta,
            {"email": email},
            f"No se pudo obtener el usuario con email {email}.",
        )

    def obtener_por_id(self, id_usuario: int):
        """Obtiene un usuario mediante su id."""

        consulta = text(f"""
            SELECT {_COLUMNAS_USUARIO}
            FROM usuarios
            WHERE id_usuario = :id_usuario
            LIMIT 1
        """)

        return self._obtener_uno(
            consulta,
            {"id_usuario": id_usuario},
            f"No se pudo obtener el usuario con id {id_usuario}.",
        )

    def crear(
        self,
        nombre: str,
        apellido,
        email: str,
        password_hash: str,
    ):
        """Inserta un usuario nuevo y devuelve sus datos públicos."""

        consulta = text(f"""
            INSERT INTO usuarios (
                nombre,
                apellido,
                email,
                password_hash
            )
            VALUES (
                :nombre,
                :apellido,
                :email,
                :password_hash
            )
            RETURNING {_COLUMNAS_USUARIO}
        """)

        parametros = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "password_hash": password_hash,
        }

        return self._crear(consulta, parametros)

    def _obtener_uno(self, consulta, parametros, mensaje_error):
        """Ejecuta una consulta y devuelve una fila o None."""

        try:
            with SessionLocal() as db:
                resultado = db.execute(consulta, parametros)
                fila = resultado.mappings().first()

                return dict(fila) if fila is not None else None

        except SQLAlchemyError as error:
            raise RuntimeError(mensaje_error) from error

    def _crear(self, consulta, parametros):
        """Ejecuta un INSERT y devuelve la fila creada."""

        try:
            with SessionLocal() as db:
                resultado = db.execute(consulta, parametros)
                fila = resultado.mappings().first()
                db.commit()

                if fila is None:
                    raise RuntimeError(
                        "No se pudo confirmar la creación del usuario."
                    )

                return dict(fila)

        except IntegrityError as error:
            raise ValueError(
                "Ya existe un usuario registrado con ese email."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudo crear el usuario en la base de datos."
            ) from error
