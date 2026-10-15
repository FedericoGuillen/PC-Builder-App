
"""
Módulo de conexión entre Python y PostgreSQL.
Permite conectar, insertar y consultar registros.
"""

import psycopg2
from psycopg2 import Error


def conectar():
    """Establece y devuelve una conexión con PostgreSQL."""
    try:
        conexion = psycopg2.connect(
            host="localhost",
            database="pc_builder_db",
            user="postgres",
            password="1234",
            port="5432"
        )
        return conexion

    except Error as error:
        print(f"Error al conectar con PostgreSQL: {error}")
        return None


def crear_tabla():
    """Crea la tabla de registros si todavía no existe."""
    conexion = conectar()

    if conexion is None:
        return

    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS marcas (
                        id_marca BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        nombre VARCHAR(100) NOT NULL UNIQUE,
                        sitio_web TEXT,
                        activo BOOLEAN NOT NULL DEFAULT TRUE
                    );
                """)
        print("Tabla creada o verificada correctamente.")

    except Error as error:
        print(f"Error al crear la tabla: {error}")

    finally:
        conexion.close()


def insertar_registro(nombre, sitio_web):
    """Inserta un registro nuevo en la base de datos."""
    conexion = conectar()

    if conexion is None:
        return False

    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO marcas (nombre, sitio_web)
                    VALUES (%s, %s);
                    """,
                    (nombre, sitio_web)
                )
        print("Registro insertado correctamente.")
        return True

    except Error as error:
        print(f"Error al insertar el registro: {error}")
        return False

    finally:
        conexion.close()


def consultar_registros():
    """Consulta y devuelve todos los registros almacenados."""
    conexion = conectar()

    if conexion is None:
        return []

    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM marcas
                    ORDER BY id;
                """)
                return cursor.fetchall()

    except Error as error:
        print(f"Error al consultar los registros: {error}")
        return []

    finally:
        conexion.close()
