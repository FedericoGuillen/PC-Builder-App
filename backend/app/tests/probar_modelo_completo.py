"""
Módulo de prueba completo para verificar conexión, lectura y escritura en PostgreSQL
para el modelo relacional central del proyecto  (Tablas 1 a 8).
"""

from app.database.conexion import engine, SessionLocal
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
    """Ejecuta inserciones y consultas relacionales en el esquema principal."""
    print("\n" + "=" * 65)
    print(" VERIFICACIÓN DE OPERACIONES EN EL ESQUEMA COMPLETO (TABLAS 1-8)")
    print("=" * 65)

    db = SessionLocal()

    try:
        # 1. MARCAS Y TIPOS
        print("\n--- 1. Pruebas en 'marcas' y 'tipos_componente' ---")
        marca_test = Marca(nombre="Marca Test DDL", sitio_web="https://test.com")
        tipo_test = TipoComponente(
            nombre="Procesador Test",
            descripcion="CPU de prueba",
            obligatorio=True,
        )

        db.add_all([marca_test, tipo_test])
        db.commit()
        db.refresh(marca_test)
        db.refresh(tipo_test)
        print(
            f"[OK] Marca (ID: {marca_test.id_marca}) y Tipo (ID: {tipo_test.id_tipo}) creados."
        )

        # 2. COMPONENTES
        print("\n--- 2. Pruebas en 'componentes' ---")
        cpu_test = Componente(
            id_marca=marca_test.id_marca,
            id_tipo=tipo_test.id_tipo,
            nombre="Intel Core i7-13700K",
            consumo_watts=125,
            precio_referencia=420.00,
            stock=10,
            especificaciones={"socket": "LGA1700", "cores": 16},
        )
        db.add(cpu_test)
        db.commit()
        db.refresh(cpu_test)
        print(
            f"[OK] Componente creado con ID: {cpu_test.id_componente} | Consumo: {cpu_test.consumo_watts}W"
        )

        # 3. USUARIOS Y CONFIGURACIONES
        print("\n--- 3. Pruebas en 'usuarios' y 'configuraciones_pc' ---")
        usuario_test = Usuario(
            nombre="Yasmin",
            apellido="Ortega",
            email="yasmine.test@ensamblapc.com",
            password_hash="hash_seguro_123",
        )
        db.add(usuario_test)
        db.commit()
        db.refresh(usuario_test)

        config_test = ConfiguracionPC(
            id_usuario=usuario_test.id_usuario,
            nombre="PC Gamer Pruebas",
            estado="BORRADOR",
            precio_total=420.00,
        )
        db.add(config_test)
        db.commit()
        db.refresh(config_test)
        print(
            f"[OK] Usuario (ID: {usuario_test.id_usuario}) y Configuración (ID: {config_test.id_configuracion}) creados."
        )

        # 4. CONFIGURACIÓN COMPONENTES (RELACIÓN N:M)
        print("\n--- 4. Pruebas en 'configuracion_componentes' ---")
        item_config = ConfiguracionComponente(
            id_configuracion=config_test.id_configuracion,
            id_componente=cpu_test.id_componente,
            cantidad=1,
            precio_al_seleccionar=cpu_test.precio_referencia,
        )
        db.add(item_config)
        db.commit()
        print(
            f"[OK] Componente asociado a la configuración. Consumo total dinámico: {config_test.consumo_total_watts}W"
        )

        # 5. REGLAS Y RESULTADOS DE COMPATIBILIDAD
        print(
            "\n--- 5. Pruebas en 'reglas_compatibilidad' y 'resultados_compatibilidad' ---"
        )
        regla_test = ReglaCompatibilidad(
            nombre="Regla Socket CPU",
            descripcion="Valida coincidencia de socket entre CPU y Motherboard",
            codigo="R_SOCKET_01",
            nivel="ERROR",
        )
        db.add(regla_test)
        db.commit()
        db.refresh(regla_test)

        resultado_test = ResultadoCompatibilidad(
            id_configuracion=config_test.id_configuracion,
            id_regla=regla_test.id_regla,
            resultado="COMPATIBLE",
            mensaje="Socket validado correctamente.",
        )
        db.add(resultado_test)
        db.commit()
        print(
            f"[OK] Regla (ID: {regla_test.id_regla}) y Resultado guardado correctamente."
        )

        # 6. LIMPIEZA AUTOMÁTICA CON ON DELETE CASCADE
        print("\n--- 6. Limpieza de datos de prueba ---")
        db.delete(
            usuario_test
        )  # Elimina en cascada la configuración, sus ítems y resultados
        db.delete(cpu_test)
        db.delete(marca_test)
        db.delete(tipo_test)
        db.delete(regla_test)
        db.commit()
        print(
            "[INFO] Registros temporales eliminados correctamente mediante la cascada ORM/SQL."
        )

        print("\n" + "=" * 65)
        print(
            " [ÉXITO] EL MODELO DE DATOS Y LAS OPERACIONES CRUD ESTÁN 100% OPERATIVOS"
        )
        print("=" * 65 + "\n")

    except Exception as error:
        db.rollback()
        print(f"\n[ERROR] Durante la prueba relacional: {error}")
    finally:
        db.close()


if __name__ == "__main__":
    probar_operaciones_modelo_completo()
