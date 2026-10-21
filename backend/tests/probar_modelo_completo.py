"""
Prueba manual de integración del modelo ORM con PostgreSQL.

Este script inserta información temporal, verifica relaciones y después
elimina los registros creados.

No forma parte del inicio normal de la aplicación.
"""

from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from app.database.conexion import SessionLocal
from app.domain.modelos import (
    Usuario,
    Marca,
    TipoComponente,
    Componente,
    ConfiguracionPC,
    ConfiguracionComponente,
    ReglaCompatibilidad,
    ResultadoCompatibilidad,
)


def probar_operaciones_modelo_completo():
    """Verifica operaciones de escritura y relaciones del modelo ORM."""

    print("\n" + "=" * 65)
    print(" VERIFICACIÓN DEL MODELO ORM")
    print("=" * 65)

    identificador = uuid4().hex[:8]

    db = SessionLocal()

    try:
        # 1. Marca y tipo
        print("\n--- 1. Marcas y tipos de componente ---")

        marca_test = Marca(
            nombre=f"Marca Test {identificador}",
            sitio_web="https://test.com",
        )

        tipo_test = TipoComponente(
            nombre=f"Procesador Test {identificador}",
            descripcion="Tipo de componente creado para una prueba manual.",
            obligatorio=True,
        )

        db.add_all([marca_test, tipo_test])
        db.flush()

        print(
            f"[OK] Marca {marca_test.id_marca} y "
            f"tipo {tipo_test.id_tipo} creados."
        )

        # 2. Componente
        print("\n--- 2. Componentes ---")

        cpu_test = Componente(
            id_marca=marca_test.id_marca,
            id_tipo=tipo_test.id_tipo,
            nombre="Intel Core i7-13700K Test",
            consumo_watts=125,
            precio_referencia=420.00,
            stock=10,
            especificaciones={
                "socket": "LGA1700",
                "cores": 16,
            },
        )

        db.add(cpu_test)
        db.flush()

        print(
            f"[OK] Componente {cpu_test.id_componente} creado."
        )

        # 3. Usuario y configuración
        print("\n--- 3. Usuarios y configuraciones ---")

        usuario_test = Usuario(
            nombre="Usuario",
            apellido="Prueba",
            email=f"prueba.{identificador}@ensamblapc.test",
            password_hash="hash_solo_para_prueba",
        )

        db.add(usuario_test)
        db.flush()

        configuracion_test = ConfiguracionPC(
            id_usuario=usuario_test.id_usuario,
            nombre="Configuración de prueba",
            estado="BORRADOR",
            precio_total=420.00,
        )

        db.add(configuracion_test)
        db.flush()

        print(
            f"[OK] Usuario {usuario_test.id_usuario} y configuración "
            f"{configuracion_test.id_configuracion} creados."
        )

        # 4. Componente de configuración
        print("\n--- 4. Componentes de configuración ---")

        item_configuracion = ConfiguracionComponente(
            id_configuracion=configuracion_test.id_configuracion,
            id_componente=cpu_test.id_componente,
            cantidad=1,
            precio_al_seleccionar=cpu_test.precio_referencia,
        )

        db.add(item_configuracion)
        db.flush()

        print("[OK] Componente asociado a la configuración.")

        # 5. Regla y resultado
        print("\n--- 5. Compatibilidad ---")

        regla_test = ReglaCompatibilidad(
            nombre=f"Regla Socket Test {identificador}",
            descripcion="Valida coincidencia de socket.",
            codigo=f"R_TEST_{identificador}",
            nivel="ERROR",
        )

        db.add(regla_test)
        db.flush()

        resultado_test = ResultadoCompatibilidad(
            id_configuracion=configuracion_test.id_configuracion,
            id_regla=regla_test.id_regla,
            resultado="COMPATIBLE",
            mensaje="Socket validado correctamente.",
        )

        db.add(resultado_test)
        db.flush()

        print(
            f"[OK] Regla {regla_test.id_regla} y resultado creados."
        )

        print("\n" + "=" * 65)
        print(" [ÉXITO] EL MODELO ORM FUNCIONA CORRECTAMENTE")
        print("=" * 65)

    except SQLAlchemyError as error:
        print(f"\n[ERROR] Falló la prueba: {error}")
        raise

    finally:
        # Esta prueba no debe dejar información temporal.
        db.rollback()
        db.close()

        print("\n[INFO] Transacción revertida y sesión cerrada.")


if __name__ == "__main__":
    probar_operaciones_modelo_completo()
