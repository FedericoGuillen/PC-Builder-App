/*
===========================================================
Proyecto: TP Final POO_3, Grupo 7.
Archivo:  07_triggers.sql
Descripción: Los triggers son mecanismos automáticos que se ejecutan cuando 
			 ocurre un evento en una tabla (INSERT, UPDATE o DELETE).
===========================================================
*/

-- 1. Recalcular el precio total automáticamente
CREATE OR REPLACE FUNCTION fn_trigger_actualizar_precio()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE configuraciones_pc
    SET precio_total =
    (
        SELECT COALESCE(
            SUM(cantidad * precio_al_seleccionar),
            0
        )
        FROM configuracion_componentes
        WHERE id_configuracion =
        COALESCE(
            NEW.id_configuracion,
            OLD.id_configuracion
        )
    )
    WHERE id_configuracion =
    COALESCE(
        NEW.id_configuracion,
        OLD.id_configuracion
    );

    RETURN NULL;

END;
$$;


CREATE TRIGGER trg_actualizar_precio_total
AFTER INSERT OR UPDATE OR DELETE
ON configuracion_componentes
FOR EACH ROW
EXECUTE FUNCTION fn_trigger_actualizar_precio();

-- 2. Actualizar fecha_modificacion
CREATE OR REPLACE FUNCTION fn_actualizar_fecha_modificacion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    NEW.fecha_modificacion :=
    CURRENT_TIMESTAMP;

    RETURN NEW;

END;
$$;


CREATE TRIGGER trg_fecha_modificacion
BEFORE UPDATE
ON configuraciones_pc
FOR EACH ROW
EXECUTE FUNCTION fn_actualizar_fecha_modificacion();


-- 3. Validar stock antes de agregar componentes
CREATE OR REPLACE FUNCTION fn_validar_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_stock INTEGER;
BEGIN

    SELECT stock
    INTO v_stock
    FROM componentes
    WHERE id_componente = NEW.id_componente;

    IF NEW.cantidad > v_stock THEN
        RAISE EXCEPTION
        'Stock insuficiente';
    END IF;

    RETURN NEW;

END;
$$;

CREATE TRIGGER trg_validar_stock
BEFORE INSERT OR UPDATE
ON configuracion_componentes
FOR EACH ROW
EXECUTE FUNCTION fn_validar_stock();


-- 4. Descontar stock automáticamente
CREATE OR REPLACE FUNCTION fn_descontar_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE componentes
    SET stock = stock - NEW.cantidad
    WHERE id_componente = NEW.id_componente;

    RETURN NEW;

END;
$$;


CREATE TRIGGER trg_descontar_stock
AFTER INSERT
ON configuracion_componentes
FOR EACH ROW
EXECUTE FUNCTION fn_descontar_stock();


-- 5. Recuperar stock al eliminar
CREATE OR REPLACE FUNCTION fn_reponer_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE componentes
    SET stock = stock + OLD.cantidad
    WHERE id_componente = OLD.id_componente;

    RETURN OLD;

END;
$$;

CREATE TRIGGER trg_reponer_stock
AFTER DELETE
ON configuracion_componentes
FOR EACH ROW
EXECUTE FUNCTION fn_reponer_stock();


-- 6. Evitar configuraciones vacías como FINALIZADAS
CREATE OR REPLACE FUNCTION fn_validar_finalizacion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cantidad INTEGER;
BEGIN

    IF NEW.estado = 'FINALIZADA' THEN

        SELECT COUNT(*)
        INTO v_cantidad
        FROM configuracion_componentes
        WHERE id_configuracion =
        NEW.id_configuracion;

        IF v_cantidad = 0 THEN
            RAISE EXCEPTION
            'No puede finalizar una configuracion vacia';
        END IF;

    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_validar_finalizacion
BEFORE UPDATE
ON configuraciones_pc
FOR EACH ROW
EXECUTE FUNCTION fn_validar_finalizacion();