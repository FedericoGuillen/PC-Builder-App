/*
===========================================================
Proyecto: TP Final POO_3, Grupo 7.
Archivo:  05_functions.sql
Descripción: Creamos funciones reutilizables que encapsulan la lógica de negocio 
 			 del configurador de PCs.
===========================================================
*/


-- 1. Calcular el precio total de una configuración
-- Esta función suma el precio de todos los componentes seleccionados.
CREATE OR REPLACE FUNCTION fn_calcular_precio_total(
    p_id_configuracion BIGINT
)
RETURNS NUMERIC(12,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC(12,2);
BEGIN
    SELECT COALESCE(
        SUM(cantidad * precio_al_seleccionar),
        0
    )
    INTO v_total
    FROM configuracion_componentes
    WHERE id_configuracion = p_id_configuracion;

    RETURN v_total;
END;
$$;


-- 2. Actualizar el precio total de una configuración
CREATE OR REPLACE FUNCTION fn_actualizar_precio_total(
    p_id_configuracion BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE configuraciones_pc
    SET precio_total = fn_calcular_precio_total(p_id_configuracion),
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id_configuracion = p_id_configuracion;
END;
$$;


-- 3. Obtener el consumo total de watts
-- Útil para validar fuentes de alimentación.
CREATE OR REPLACE FUNCTION fn_consumo_total_configuracion(
    p_id_configuracion BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_total INTEGER;
BEGIN
    SELECT COALESCE(
        SUM(c.consumo_watts * cc.cantidad),
        0
    )
    INTO v_total
    FROM configuracion_componentes cc
    JOIN componentes c
        ON c.id_componente = cc.id_componente
    WHERE cc.id_configuracion = p_id_configuracion;

    RETURN v_total;
END;
$$;


-- 4. Verificar si existe una GPU
CREATE OR REPLACE FUNCTION fn_tiene_gpu(
    p_id_configuracion BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_existe BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1
        FROM configuracion_componentes cc
        JOIN componentes c
            ON c.id_componente = cc.id_componente
        WHERE cc.id_configuracion = p_id_configuracion
        AND c.id_tipo = 6
    )
    INTO v_existe;

    RETURN v_existe;
END;
$$;


-- 5. Obtener el componente más caro de una configuración
CREATE OR REPLACE FUNCTION fn_componente_mas_caro(
    p_id_configuracion BIGINT
)
RETURNS TABLE(
    componente VARCHAR(200),
    precio NUMERIC(12,2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.nombre,
        cc.precio_al_seleccionar
    FROM configuracion_componentes cc
    JOIN componentes c
        ON c.id_componente = cc.id_componente
    WHERE cc.id_configuracion = p_id_configuracion
    ORDER BY cc.precio_al_seleccionar DESC
    LIMIT 1;
END;
$$;

-- 6. Contar componentes de una configuración
CREATE OR REPLACE FUNCTION fn_cantidad_componentes(
    p_id_configuracion BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cantidad INTEGER;
BEGIN
    SELECT COALESCE(SUM(cantidad),0)
    INTO v_cantidad
    FROM configuracion_componentes
    WHERE id_configuracion = p_id_configuracion;

    RETURN v_cantidad;
END;
$$;


-- 7. Obtener el stock disponible de un componente
CREATE OR REPLACE FUNCTION fn_stock_componente(
    p_id_componente BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_stock INTEGER;
BEGIN
    SELECT stock
    INTO v_stock
    FROM componentes
    WHERE id_componente = p_id_componente;

    RETURN v_stock;
END;
$$;


-- 11. Funcion parametrizada consumible desde PerfilRepository.
CREATE OR REPLACE FUNCTION fn_componentes_por_perfil(
    p_id_perfil BIGINT,
    p_id_tipo BIGINT DEFAULT NULL,
    p_precio_maximo NUMERIC DEFAULT NULL,
    p_solo_recomendados BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    id_componente BIGINT,
    categoria VARCHAR,
    marca VARCHAR,
    nombre VARCHAR,
    modelo VARCHAR,
    precio_referencia NUMERIC,
    stock INTEGER,
    especificaciones JSONB,
    afinidad SMALLINT,
    obligatorio BOOLEAN
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        v.id_componente,
        v.categoria,
        v.marca,
        v.nombre,
        v.modelo,
        v.precio_referencia,
        v.stock,
        v.especificaciones,
        v.afinidad,
        v.obligatorio
    FROM vw_componentes_por_perfil v
    WHERE v.id_perfil = p_id_perfil
      AND (p_id_tipo IS NULL OR v.id_tipo = p_id_tipo)
      AND (p_precio_maximo IS NULL OR v.precio_referencia <= p_precio_maximo)
      AND (NOT p_solo_recomendados OR v.recomendado)
    ORDER BY v.prioridad DESC, v.categoria, v.afinidad DESC,
             v.precio_referencia NULLS LAST;
$$;


-- Consultas de verificacion:
-- SELECT * FROM perfiles_uso ORDER BY orden_visual;
-- SELECT * FROM vw_componentes_por_perfil ORDER BY perfil, categoria, afinidad DESC;
-- SELECT * FROM fn_componentes_por_perfil(1, NULL, NULL, TRUE);
