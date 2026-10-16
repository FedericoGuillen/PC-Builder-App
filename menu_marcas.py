
"""
Aplicación principal para la gestión de marcas.

Permite listar, crear, activar y desactivar marcas
almacenadas en PostgreSQL.
"""

from conexion import conectar


def listar_marcas():
    """Muestra todas las marcas registradas en la base de datos."""
    conexion = conectar()

    if conexion is None:
        print("Error: no se pudo conectar a la base de datos.")
        return

    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id_marca, nombre, sitio_web, activo
                FROM marcas
                ORDER BY id_marca;
            """)

            marcas = cursor.fetchall()

        if not marcas:
            print("\nNo hay marcas registradas.")
            return

        print("\n" + "=" * 85)
        print("LISTADO DE MARCAS")
        print("=" * 85)

        for id_marca, nombre, sitio_web, activo in marcas:
            estado = "Activa" if activo else "Inactiva"
            sitio = sitio_web or "Sin sitio web"

            print(f"ID: {id_marca}")
            print(f"Nombre: {nombre}")
            print(f"Sitio web: {sitio}")
            print(f"Estado: {estado}")
            print("-" * 85)

    except Exception as error:
        print(f"Error al consultar las marcas: {error}")

    finally:
        conexion.close()


def crear_marca():
    """Registra una nueva marca."""
    print("\n--- CREAR MARCA ---")

    nombre = input("Nombre de la marca: ").strip()

    if not nombre:
        print("Error: el nombre es obligatorio.")
        return

    sitio_web = input(
        "Sitio web (opcional, presioná Enter para omitirlo): "
    ).strip()

    sitio_web = sitio_web or None

    conexion = conectar()

    if conexion is None:
        print("Error: no se pudo conectar a la base de datos.")
        return

    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO marcas (nombre, sitio_web)
                    VALUES (%s, %s)
                    RETURNING id_marca, nombre, sitio_web, activo;
                """, (nombre, sitio_web))

                marca = cursor.fetchone()

        print("\nMarca creada correctamente.")
        print(f"ID: {marca[0]}")
        print(f"Nombre: {marca[1]}")
        print(f"Sitio web: {marca[2] or 'Sin sitio web'}")
        print(f"Estado: {'Activa' if marca[3] else 'Inactiva'}")

    except Exception as error:
        print(f"Error al crear la marca: {error}")

    finally:
        conexion.close()


def cambiar_estado_marca():
    """Activa o desactiva una marca existente."""
    print("\n--- CAMBIAR ESTADO DE MARCA ---")

    try:
        id_marca = int(input("ID de la marca: ").strip())
    except ValueError:
        print("Error: ingresá un ID numérico válido.")
        return

    if id_marca <= 0:
        print("Error: el ID debe ser mayor que cero.")
        return

    print("1. Activar marca")
    print("2. Desactivar marca")

    opcion = input("Seleccioná una opción: ").strip()

    if opcion not in ("1", "2"):
        print("Opción inválida.")
        return

    nuevo_estado = opcion == "1"

    conexion = conectar()

    if conexion is None:
        print("Error: no se pudo conectar a la base de datos.")
        return

    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    UPDATE marcas
                    SET activo = %s
                    WHERE id_marca = %s
                    RETURNING id_marca, nombre, activo;
                """, (nuevo_estado, id_marca))

                marca = cursor.fetchone()

        if marca is None:
            print(f"No existe una marca con ID {id_marca}.")
        else:
            estado = "Activa" if marca[2] else "Inactiva"
            print(f"Marca '{marca[1]}' actualizada: {estado}.")

    except Exception as error:
        print(f"Error al actualizar la marca: {error}")

    finally:
        conexion.close()


def mostrar_menu():
    """Presenta el menú principal de la aplicación."""
    while True:
        print("\n" + "=" * 45)
        print("       SISTEMA DE GESTIÓN DE MARCAS")
        print("=" * 45)
        print("1. Listar marcas")
        print("2. Crear marca")
        print("3. Activar o desactivar marca")
        print("0. Salir")
        print("=" * 45)

        opcion = input("Seleccioná una opción: ").strip()

        if opcion == "1":
            listar_marcas()
        elif opcion == "2":
            crear_marca()
        elif opcion == "3":
            cambiar_estado_marca()
        elif opcion == "0":
            print("Aplicación finalizada.")
            break
        else:
            print("Opción inválida. Intentá nuevamente.")


def main():
    """Punto de entrada de la aplicación."""
    mostrar_menu()


if __name__ == "__main__":
    main()
