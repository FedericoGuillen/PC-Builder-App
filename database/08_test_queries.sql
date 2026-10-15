/*
===========================================================
Proyecto: TP Final POO_3, Grupo 7.
Archivo:  08_test_queries.sql
Descripción: Demostramos que la BD funciona correctamente.
===========================================================
*/

-- 1. Test de tablas
-- Usuarios
SELECT * FROM usuarios;

-- Marcas
SELECT * FROM marcas;

-- Tipos de componentes
SELECT * FROM tipos_componente;

-- Componentes
SELECT * FROM componentes;


-- 2. Test de consultas básicas
-- CPUs disponibles
SELECT nombre, modelo, precio_referencia
FROM componentes
WHERE id_tipo = 1;

-- Componentes con stock
SELECT nombre, modelo, stock
FROM componentes
WHERE stock > 0;


-- Componentes ordenados por precio
SELECT nombre,
       modelo,
       precio_referencia
FROM componentes
ORDER BY precio_referencia DESC;


-- 3. Crear una configuración de prueba
CALL sp_crear_configuracion(
    1,
    'PC Gamer Test',
    'Configuracion para pruebas'
);

-- Verificamos con
SELECT *
FROM configuraciones_pc;


-- 4. Agregar componentes
CALL sp_agregar_componente(
    1,
    1,
    1
); -- CPU Ryzen 5.

CALL sp_agregar_componente(
    1,
    9,
    1
); -- Motherboard ASUS.

CALL sp_agregar_componente(
    1,
    13,
    1
); -- RAM

-- Verificamos con 
SELECT *
FROM configuracion_componentes;


-- 5. Test de funciones
-- PRECIO TOTAL
SELECT fn_calcular_precio_total(1);

-- CONSUMO TOTAL
SELECT fn_consumo_total_configuracion(1);

-- CANTIDAD DE COMPONENTES
SELECT fn_cantidad_componentes(1);

-- SI TIENE GPU
SELECT fn_tiene_gpu(1);


-- 6. Test de trigger de precio total
-- Primero hacer
SELECT precio_total
FROM configuraciones_pc
WHERE id_configuracion = 1;

-- Luego agregar una GPU
CALL sp_agregar_componente(
    1,
    21,
    1
);

-- Volvemos a consultar y el valor deberia haber cambiado
SELECT precio_total
FROM configuraciones_pc
WHERE id_configuracion = 1;

-- 7. Test de trigger de stock
-- Consultamos el stock
SELECT stock
FROM componentes
WHERE id_componente = 21;

-- Agregamos la GPU
CALL sp_agregar_componente(
    1,
    21,
    1
);


-- Consultamos stock nuevamente y deberia haberse reducido
SELECT stock
FROM componentes
WHERE id_componente = 21;


-- 8. Test de validación de stock
-- Intentar agregar más unidades de las disponibles:
CALL sp_agregar_componente(
    1,
    21,
    999
);


-- 9. Test de finalización
CALL sp_finalizar_configuracion(1);

-- Verificamos con 
SELECT estado
FROM configuraciones_pc
WHERE id_configuracion = 1;