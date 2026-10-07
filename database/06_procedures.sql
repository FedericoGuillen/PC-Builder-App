/*
===========================================================
Proyecto: TP Final POO_3, Grupo 7.
Archivo:  06_procedures.sql
Descripción: Los procedures (procedimientos almacenados) sirven para ejecutar 
			 acciones completas sobre la base de datos
===========================================================
*/

-- 1. Crear una configuración nueva
CREATE OR REPLACE PROCEDURE sp_crear_configuracion(
    p_id_usuario BIGINT,
    p_nombre VARCHAR(150),
    p_descripcion TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO configuraciones_pc(
        id_usuario,
        nombre,
        descripcion
    )
    VALUES (
        p_id_usuario,
        p_nombre,
        p_descripcion
    );
END;
$$;

-- 2. Agregar un componente a una configuración
CREATE OR REPLACE PROCEDURE sp_agregar_componente(
    p_id_configuracion BIGINT,
    p_id_componente BIGINT,
    p_cantidad INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_precio NUMERIC(12,2);
BEGIN

    SELECT precio_referencia
    INTO v_precio
    FROM componentes
    WHERE id_componente = p_id_componente;

    INSERT INTO configuracion_componentes(
        id_configuracion,
        id_componente,
        cantidad,
        precio_al_seleccionar
    )
    VALUES (
        p_id_configuracion,
        p_id_componente,
        p_cantidad,
        v_precio
    );

END;
$$;


-- 3. Eliminar un componente de una configuración
CREATE OR REPLACE PROCEDURE sp_eliminar_componente(
    p_id_configuracion BIGINT,
    p_id_componente BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN

    DELETE FROM configuracion_componentes
    WHERE id_configuracion = p_id_configuracion
    AND id_componente = p_id_componente;

END;
$$;


-- 4. Finalizar una configuración
CREATE OR REPLACE PROCEDURE sp_finalizar_configuracion(
    p_id_configuracion BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE configuraciones_pc
    SET estado = 'FINALIZADA',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id_configuracion = p_id_configuracion;

END;
$$;


-- 5. Actualizar automáticamente el precio total
CREATE OR REPLACE PROCEDURE sp_recalcular_total(
    p_id_configuracion BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE configuraciones_pc
    SET precio_total =
        fn_calcular_precio_total(
            p_id_configuracion
        )
    WHERE id_configuracion =
        p_id_configuracion;

END;
$$;

-- 6. Registrar una incompatibilidad
CREATE OR REPLACE PROCEDURE sp_registrar_incompatibilidad(
    p_id_configuracion BIGINT,
    p_id_regla BIGINT,
    p_mensaje TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO resultados_compatibilidad(
        id_configuracion,
        id_regla,
        resultado,
        mensaje
    )
    VALUES (
        p_id_configuracion,
        p_id_regla,
        'INCOMPATIBLE',
        p_mensaje
    );

END;
$$;