/*
===========================================================
Proyecto: TP Final POO_3, Grupo 7.
Archivo:  04_views.sql
Descripción: Vistas que simplifican las consultas frecuentes del sistema de 
			 armado de PCs.
===========================================================
*/

-- Vista del catálogo completo
-- . Vista plana para el catalogo de la aplicacion.
CREATE OR REPLACE VIEW vw_catalogo_componentes AS
SELECT
    c.id_componente,
    t.id_tipo,
    t.nombre AS categoria,
    m.id_marca,
    m.nombre AS marca,
    c.nombre,
    c.modelo,
    c.descripcion,
    c.consumo_watts,
    c.precio_referencia,
    c.stock,
    c.especificaciones,
    c.imagen_url
FROM componentes c
JOIN tipos_componente t ON t.id_tipo = c.id_tipo
JOIN marcas m ON m.id_marca = c.id_marca
WHERE c.activo = TRUE AND m.activo = TRUE;

-- . Vista de componentes adecuados para cada perfil.
CREATE OR REPLACE VIEW vw_componentes_por_perfil AS
SELECT
    p.id_perfil,
    p.codigo AS perfil_codigo,
    p.nombre AS perfil,
    v.*,
    pc.afinidad,
    pc.recomendado,
    pc.observacion,
    pt.obligatorio,
    pt.prioridad,
    pt.cantidad_sugerida
FROM perfiles_uso p
JOIN perfil_componentes pc ON pc.id_perfil = p.id_perfil
JOIN vw_catalogo_componentes v ON v.id_componente = pc.id_componente
JOIN perfil_tipos_componente pt
  ON pt.id_perfil = p.id_perfil AND pt.id_tipo = v.id_tipo
WHERE p.activo = TRUE;

-- Vista de CPUs
CREATE VIEW vw_cpus AS
SELECT
    id_componente,
    nombre,
    modelo,
    especificaciones->>'socket' AS socket,
    especificaciones->>'arquitectura' AS arquitectura,
    precio_referencia
FROM componentes
WHERE id_tipo = 1;

-- Vista de Motherboards
CREATE VIEW vw_motherboards AS
SELECT
    id_componente,
    nombre,
    modelo,
    especificaciones->>'socket' AS socket,
    especificaciones->>'chipset' AS chipset,
    especificaciones->>'form_factor' AS form_factor,
    precio_referencia
FROM componentes
WHERE id_tipo = 3;

-- Vista CPU ↔ Motherboard compatibles
-- Muestra la compatibilidad entre CPUs y Motherboards
CREATE VIEW vw_cpu_motherboard_compatibles AS
SELECT
    cpu.id_componente AS id_cpu,
    cpu.nombre || ' ' || cpu.modelo AS cpu,
    mb.id_componente AS id_motherboard,
    mb.nombre || ' ' || mb.modelo AS motherboard,
    cpu.especificaciones->>'socket' AS socket
FROM componentes cpu
JOIN componentes mb
ON cpu.especificaciones->>'socket'
   = mb.especificaciones->>'socket'
WHERE cpu.id_tipo = 1
AND mb.id_tipo = 3;

-- Vista de GPUs con PSUs
CREATE VIEW vw_gpu_requerimientos AS
SELECT
    nombre,
    modelo,
    especificaciones->>'vram_gb' AS vram,
    especificaciones->>'fuente_recomendada_w'
        AS fuente_recomendada
FROM componentes
WHERE id_tipo = 6;

-- Vista de precios por tienda
CREATE VIEW vw_precios_componentes AS
SELECT
    c.nombre,
    c.modelo,
    t.nombre AS tienda,
    pc.precio,
    pc.moneda,
    pc.disponible
FROM precios_componentes pc
JOIN componentes c
    ON pc.id_componente = c.id_componente
JOIN tiendas t
    ON pc.id_tienda = t.id_tienda;

-- Vista del precio más barato por componente
CREATE VIEW vw_mejor_precio AS
SELECT
    c.id_componente,
    c.nombre,
    c.modelo,
    MIN(pc.precio) AS mejor_precio
FROM componentes c
JOIN precios_componentes pc
    ON c.id_componente = pc.id_componente
GROUP BY
    c.id_componente,
    c.nombre,
    c.modelo;


