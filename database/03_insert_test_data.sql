/*
===========================================================
Proyecto: TP Final POO_3, Grupo 7.
Archivo: 03_insert_test_data.sql
Descripción: Inserción de datos a cada tabla.
===========================================================
*/

-- Inserción de "Tipos de Componentes" en la tabla 'tipos_componente'

INSERT INTO tipos_componente
(nombre, descripcion, cantidad_maxima_sugerida, obligatorio)
VALUES

('CPU', 'Procesador principal del sistema', 1, TRUE),
('CPU_COOLER', 'Sistema de refrigeración para el procesador', 1, FALSE),
('MOTHERBOARD', 'Placa madre donde se conectan todos los componentes', 1, TRUE),
('RAM', 'Memoria principal del sistema', 4, TRUE),
('STORAGE', 'Dispositivos de almacenamiento SSD o HDD', 8, TRUE),
('GPU', 'Tarjeta gráfica dedicada', 4, FALSE),
('PSU', 'Fuente de alimentación', 1, TRUE),
('CASE', 'Gabinete que contiene los componentes', 1, TRUE),

-- EXTRAS
('CASE_FAN',  'Ventiladores del gabinete',  10, FALSE), 
('OPTICAL_DRIVE', 'Lectora o grabadora óptica', 2, FALSE),
('SOUND_CARD', 'Tarjeta de sonido dedicada', 2, FALSE),
('NETWORK_CARD', 'Tarjeta de red dedicada', 2, FALSE);


-- Inserción de "Marcas de componentes" en la tabla 'marcas'
INSERT INTO marcas
(nombre, sitio_web)
VALUES
('AMD', 'https://www.amd.com'),
('Intel', 'https://www.intel.com'),
('ASUS', 'https://www.asus.com'),
('MSI', 'https://www.msi.com'),
('Gigabyte', 'https://www.gigabyte.com'),
('NVIDIA', 'https://www.nvidia.com'),
('Corsair', 'https://www.corsair.com'),
('Kingston', 'https://www.kingston.com'),
('Samsung', 'https://www.samsung.com'),
('Western Digital', 'https://www.westerndigital.com'),
('Cooler Master', 'https://www.coolermaster.com'),
('DeepCool', 'https://www.deepcool.com'),
('Noctua', 'https://www.noctua.at'),
('EVGA', 'https://www.evga.com'),
('NZXT', 'https://nzxt.com');

-- Inserto los componentes
-- CPUs
INSERT INTO componentes (
    id_tipo,
    id_marca,
    nombre,
    modelo,
    descripcion,
    consumo_watts,
    precio_referencia,
    stock,
    especificaciones
)
VALUES (
    1,
    1,
    'AMD Ryzen 5',
    '7600',
    'Procesador AMD Ryzen 5 7600 para socket AM5',
    65,
    280000,
    10,
    '{
        "socket":"AM5",
        "arquitectura":"Zen 4",
        "nucleos":6,
        "hilos":12,
        "frecuencia_base":3.8,
        "frecuencia_boost":5.1,
        "ram_tipo":["DDR4", "DDR5"],
        "pcie":"5.0",
        "gpu_integrada":true
    }'::jsonb
),
(   1,
    1,
    'AMD Ryzen 7',
    '7700X',
    'Procesador AMD Ryzen 7 7700X para socket AM5',
    105,
    280000,
    10,
    '{
        "socket":"AM5",
        "arquitectura":"Zen 4",
        "nucleos":8,
        "hilos":16,
        "frecuencia_base":4.5,
        "frecuencia_boost":5.4,
        "ram_tipo":["DDR4", "DDR5"],
        "pcie":"5.0",
        "gpu_integrada":true
    }'::jsonb
),
(	1,
    2,
    'Intel Core i5',
    '14600K',
    'Procesador Intel Core i5 14600K para socket LGA1700',
    125,
    300000,
    10,
    '{
        "socket":"LGA1700",
        "arquitectura":"Raptor Lake Refresh",
        "nucleos":14,
        "hilos":20,
        "frecuencia_base":3.5,
        "frecuencia_boost":5.3,
        "ram_tipo":["DDR4", "DDR5"],
        "pcie":"5.0",
        "gpu_integrada":true
    }'::jsonb
),
(	1,
    2,
    'Intel Core i7',
    '14700K',
    'Procesador Intel Core i7 14700K para socket LGA1700',
    125,
    400000,
    10,
    '{
        "socket":"LGA1700",
        "arquitectura":"Raptor Lake Refresh",
        "nucleos":20,
        "hilos":28,
        "frecuencia_base":3.4,
        "frecuencia_boost":5.6,
        "ram_tipo":["DDR4", "DDR5"],
        "pcie":"5.0",
        "gpu_integrada":true
    }'::jsonb
);

-- CPU Coolers
INSERT INTO componentes (
    id_tipo,
    id_marca,
    nombre,
    modelo,
    descripcion,
    consumo_watts,
    precio_referencia,
    stock,
    especificaciones
)
VALUES
(
    2,
    11,
    'Cooler Master Hyper 212',
    'Black Edition',
    'Cooler por aire compatible con AM5 y LGA1700',
    3,
    65000,
    10,
    '{
        "tipo":"AIRE",
        "socket":["AM5","LGA1700"],
        "tdp_max":180,
        "altura_mm":159
    }'::jsonb
),
(
    2,
    12,
    'DeepCool',
    'AK400',
    'Cooler por aire de torre simple',
    2,
    55000,
    10,
    '{
        "tipo":"AIRE",
        "socket":["AM5","LGA1700"],
        "tdp_max":220,
        "altura_mm":155
    }'::jsonb
),
(
    2,
    7,
    'Corsair',
    'H100 RGB',
    'Refrigeracion liquida AIO de 240mm',
    6,
    140000,
    5,
    '{
        "tipo":"LIQUIDO",
        "socket":["AM5","LGA1700"],
        "radiador_mm":240,
        "tdp_max":250
    }'::jsonb
),
(
    2,
    15,
    'NZXT Kraken',
    '240',
    'Refrigeracion liquida AIO premium',
    7,
    170000,
    5,
    '{
        "tipo":"LIQUIDO",
        "socket":["AM5","LGA1700"],
        "radiador_mm":240,
        "tdp_max":280
    }'::jsonb
);

-- Motherboards
INSERT INTO componentes (
    id_tipo,
    id_marca,
    nombre,
    modelo,
    descripcion,
    consumo_watts,
    precio_referencia,
    stock,
    especificaciones
)
VALUES
(
    3,
    3,
    'ASUS TUF Gaming',
    'B650-PLUS WIFI',
    'Motherboard AM5 chipset B650',
    70,
    250000,
    10,
    '{
        "socket":"AM5",
        "chipset":"B650",
        "form_factor":"ATX",
        "ram_tipo":["DDR5"],
        "ram_slots":4,
        "ram_max_gb":192,
        "pcie":"5.0",
        "m2_slots":3
    }'::jsonb
),
(
    3,
    4,
    'MSI MAG',
    'B650 Tomahawk WIFI',
    'Motherboard AM5 de gama media-alta',
    75,
    280000,
    10,
    '{
        "socket":"AM5",
        "chipset":"B650",
        "form_factor":"ATX",
        "ram_tipo":["DDR5"],
        "ram_slots":4,
        "ram_max_gb":192,
        "pcie":"5.0",
        "m2_slots":3
    }'::jsonb
),
(
    3,
    3,
    'ASUS Prime',
    'Z790-P WIFI',
    'Motherboard Intel LGA1700 chipset Z790',
    80,
    320000,
    10,
    '{
        "socket":"LGA1700",
        "chipset":"Z790",
        "form_factor":"ATX",
        "ram_tipo":["DDR5"],
        "ram_slots":4,
        "ram_max_gb":192,
        "pcie":"5.0",
        "m2_slots":4
    }'::jsonb
),
(
    3,
    5,
    'Gigabyte Gaming X',
    'Z790 X AX',
    'Motherboard Intel LGA1700 para gaming',
    75,
    300000,
    10,
    '{
        "socket":"LGA1700",
        "chipset":"Z790",
        "form_factor":"ATX",
        "ram_tipo":["DDR5"],
        "ram_slots":4,
        "ram_max_gb":192,
        "pcie":"5.0",
        "m2_slots":4
    }'::jsonb
);

-- RAM
INSERT INTO componentes (
    id_tipo,
    id_marca,
    nombre,
    modelo,
    descripcion,
    consumo_watts,
    precio_referencia,
    stock,
    especificaciones
)
VALUES
(
    4,
    8,
    'Kingston Fury Beast',
    'DDR5-5600 32GB',
    'Kit 2x16GB DDR5 para gaming y productividad',
    10,
    120000,
    15,
    '{
        "tipo":"DDR5",
        "capacidad_gb":32,
        "modulos":2,
        "velocidad_mhz":5600,
        "latencia":"CL40"
    }'::jsonb
),
(
    4,
    8,
    'Kingston Fury Beast',
    'DDR5-6000 32GB',
    'Kit 2x16GB DDR5 de alto rendimiento',
    10,
    145000,
    10,
    '{
        "tipo":"DDR5",
        "capacidad_gb":32,
        "modulos":2,
        "velocidad_mhz":6000,
        "latencia":"CL36"
    }'::jsonb
),
(
    4,
    9,
    'Samsung',
    'DDR5-5600 16GB',
    'Kit 2x8GB DDR5 para equipos de entrada',
    8,
    70000,
    20,
    '{
        "tipo":"DDR5",
        "capacidad_gb":16,
        "modulos":2,
        "velocidad_mhz":5600,
        "latencia":"CL40"
    }'::jsonb
),
(
    4,
    7,
    'Corsair Vengeance',
    'DDR5-6400 64GB',
    'Kit 2x32GB DDR5 para estaciones de trabajo',
    12,
    260000,
    5,
    '{
        "tipo":"DDR5",
        "capacidad_gb":64,
        "modulos":2,
        "velocidad_mhz":6400,
        "latencia":"CL32"
    }'::jsonb
);


-- Storage
INSERT INTO componentes (
    id_tipo,
    id_marca,
    nombre,
    modelo,
    descripcion,
    consumo_watts,
    precio_referencia,
    stock,
    especificaciones
)
VALUES
(
    5,
    9,
    'Samsung SSD',
    '990 PRO 1TB',
    'SSD NVMe PCIe 4.0 de alto rendimiento',
    6,
    120000,
    15,
    '{
        "tipo":"SSD_NVME",
        "capacidad_gb":1000,
        "interfaz":"PCIe 4.0 x4",
        "factor_forma":"M.2 2280",
        "velocidad_lectura_mbps":7450,
        "velocidad_escritura_mbps":6900
    }'::jsonb
),
(
    5,
    10,
    'WD Black',
    'SN850X 1TB',
    'SSD NVMe PCIe 4.0 para gaming',
    6,
    115000,
    15,
    '{
        "tipo":"SSD_NVME",
        "capacidad_gb":1000,
        "interfaz":"PCIe 4.0 x4",
        "factor_forma":"M.2 2280",
        "velocidad_lectura_mbps":7300,
        "velocidad_escritura_mbps":6300
    }'::jsonb
),
(
    5,
    9,
    'Samsung SSD',
    '990 EVO 2TB',
    'SSD NVMe de gran capacidad',
    6,
    180000,
    10,
    '{
        "tipo":"SSD_NVME",
        "capacidad_gb":2000,
        "interfaz":"PCIe 4.0 x4",
        "factor_forma":"M.2 2280",
        "velocidad_lectura_mbps":5000,
        "velocidad_escritura_mbps":4200
    }'::jsonb
),
(
    5,
    10,
    'WD Blue',
    'SA510 1TB',
    'SSD SATA para almacenamiento general',
    4,
    85000,
    20,
    '{
        "tipo":"SSD_SATA",
        "capacidad_gb":1000,
        "interfaz":"SATA III",
        "factor_forma":"2.5",
        "velocidad_lectura_mbps":560,
        "velocidad_escritura_mbps":520
    }'::jsonb
);


-- GPUs
INSERT INTO componentes (
    id_tipo,
    id_marca,
    nombre,
    modelo,
    descripcion,
    consumo_watts,
    precio_referencia,
    stock,
    especificaciones
)
VALUES
(
    6,
    6,
    'NVIDIA GeForce RTX',
    '4060 8GB',
    'Tarjeta gráfica para gaming en 1080p',
    115,
    450000,
    10,
    '{
        "vram_gb":8,
        "tipo_memoria":"GDDR6",
        "pcie":"4.0 x8",
        "salidas_video":["HDMI","DisplayPort"],
        "longitud_mm":245,
        "fuente_recomendada_w":550
    }'::jsonb
),
(
    6,
    6,
    'NVIDIA GeForce RTX',
    '4070 SUPER 12GB',
    'Tarjeta gráfica para gaming en 1440p',
    220,
    850000,
    8,
    '{
        "vram_gb":12,
        "tipo_memoria":"GDDR6X",
        "pcie":"4.0 x16",
        "salidas_video":["HDMI","DisplayPort"],
        "longitud_mm":300,
        "fuente_recomendada_w":650
    }'::jsonb
),
(
    6,
    6,
    'NVIDIA GeForce RTX',
    '4080 SUPER 16GB',
    'Tarjeta gráfica de alto rendimiento para 4K',
    320,
    1600000,
    5,
    '{
        "vram_gb":16,
        "tipo_memoria":"GDDR6X",
        "pcie":"4.0 x16",
        "salidas_video":["HDMI","DisplayPort"],
        "longitud_mm":310,
        "fuente_recomendada_w":850
    }'::jsonb
),
(
    6,
    6,
    'NVIDIA GeForce RTX',
    '4090 24GB',
    'Tarjeta gráfica entusiasta para gaming y IA',
    450,
    2500000,
    3,
    '{
        "vram_gb":24,
        "tipo_memoria":"GDDR6X",
        "pcie":"4.0 x16",
        "salidas_video":["HDMI","DisplayPort"],
        "longitud_mm":336,
        "fuente_recomendada_w":1000
    }'::jsonb
);

-- PSUs
INSERT INTO componentes (
    id_tipo,
    id_marca,
    nombre,
    modelo,
    descripcion,
    consumo_watts,
    precio_referencia,
    stock,
    especificaciones
)
VALUES
(
    7,
    7,
    'Corsair',
    'RM650e',
    'Fuente de alimentación 650W 80 Plus Gold',
    0,
    120000,
    10,
    '{
        "potencia_w":650,
        "certificacion":"80+ Gold",
        "modular":true,
        "factor_forma":"ATX"
    }'::jsonb
),
(
    7,
    14,
    'EVGA',
    'SuperNOVA 750 G6',
    'Fuente de alimentación 750W 80 Plus Gold',
    0,
    150000,
    10,
    '{
        "potencia_w":750,
        "certificacion":"80+ Gold",
        "modular":true,
        "factor_forma":"ATX"
    }'::jsonb
),
(
    7,
    7,
    'Corsair',
    'RM850x',
    'Fuente de alimentación 850W 80 Plus Gold',
    0,
    190000,
    8,
    '{
        "potencia_w":850,
        "certificacion":"80+ Gold",
        "modular":true,
        "factor_forma":"ATX"
    }'::jsonb
),
(
    7,
    14,
    'EVGA',
    'SuperNOVA 1000 G7',
    'Fuente de alimentación 1000W 80 Plus Gold',
    0,
    250000,
    5,
    '{
        "potencia_w":1000,
        "certificacion":"80+ Gold",
        "modular":true,
        "factor_forma":"ATX"
    }'::jsonb
);

-- Cases
INSERT INTO componentes (
    id_tipo,
    id_marca,
    nombre,
    modelo,
    descripcion,
    consumo_watts,
    precio_referencia,
    stock,
    especificaciones
)
VALUES
(
    8,
    15,
    'NZXT',
    'H5 Flow',
    'Gabinete ATX con panel frontal de alto flujo de aire',
    0,
    120000,
    10,
    '{
        "form_factor":["ATX","Micro-ATX","Mini-ITX"],
        "gpu_max_mm":365,
        "cpu_cooler_max_mm":165,
        "radiador_frontal_mm":280,
        "radiador_superior_mm":240
    }'::jsonb
),
(
    8,
    7,
    'Corsair',
    '4000D Airflow',
    'Gabinete ATX optimizado para refrigeracion',
    0,
    140000,
    10,
    '{
        "form_factor":["ATX","Micro-ATX","Mini-ITX"],
        "gpu_max_mm":360,
        "cpu_cooler_max_mm":170,
        "radiador_frontal_mm":360,
        "radiador_superior_mm":280
    }'::jsonb
),
(
    8,
    11,
    'Cooler Master',
    'MasterBox TD500 Mesh',
    'Gabinete ATX con panel frontal mesh',
    0,
    150000,
    8,
    '{
        "form_factor":["ATX","Micro-ATX","Mini-ITX"],
        "gpu_max_mm":410,
        "cpu_cooler_max_mm":165,
        "radiador_frontal_mm":360,
        "radiador_superior_mm":360
    }'::jsonb
),
(
    8,
    3,
    'ASUS',
    'TUF Gaming GT302',
    'Gabinete ATX para equipos gaming de alto rendimiento',
    0,
    180000,
    5,
    '{
        "form_factor":["ATX","Micro-ATX","Mini-ITX"],
        "gpu_max_mm":407,
        "cpu_cooler_max_mm":165,
        "radiador_frontal_mm":360,
        "radiador_superior_mm":360
    }'::jsonb
);


-- Inserto las reglas de compatibilidad
INSERT INTO reglas_compatibilidad
(nombre, descripcion, codigo, nivel)
VALUES
(
    'Compatibilidad CPU - Motherboard',
    'El socket del procesador debe coincidir con el socket de la motherboard',
    'CPU_MB_SOCKET',
    'ERROR'
),
(
    'Compatibilidad RAM - Motherboard',
    'El tipo de memoria RAM debe estar soportado por la motherboard',
    'RAM_MB_TIPO',
    'ERROR'
),
(
    'Capacidad maxima de RAM',
    'La capacidad total de RAM no debe superar la soportada por la motherboard',
    'RAM_MB_CAPACIDAD',
    'ERROR'
),
(
    'Compatibilidad Cooler - CPU',
    'El cooler debe soportar el socket del procesador',
    'COOLER_CPU_SOCKET',
    'ERROR'
),
(
    'Compatibilidad GPU - Motherboard',
    'La motherboard debe disponer de una interfaz PCIe compatible con la GPU',
    'GPU_MB_PCIE',
    'ERROR'
),
(
    'Potencia de PSU suficiente',
    'La fuente debe suministrar la potencia requerida por la configuracion',
    'PSU_POTENCIA',
    'ERROR'
),
(
    'Compatibilidad Motherboard - Case',
    'El gabinete debe soportar el factor de forma de la motherboard',
    'CASE_MB_FORM_FACTOR',
    'ERROR'
),
(
    'Espacio para GPU',
    'El gabinete debe soportar la longitud de la GPU instalada',
    'CASE_GPU_LONGITUD',
    'ERROR'
),
(
    'Altura de CPU Cooler',
    'El gabinete debe soportar la altura del cooler',
    'CASE_COOLER_ALTURA',
    'ERROR'
),
(
    'Compatibilidad SSD NVMe',
    'La motherboard debe tener slots M.2 disponibles para SSD NVMe',
    'STORAGE_M2',
    'ADVERTENCIA'
);



-- A). Carga idempotente de los tres perfiles visibles en la UI.
INSERT INTO perfiles_uso
    (codigo, nombre, descripcion, texto_destacado, orden_visual)
VALUES
    ('GAMING_STREAMING', 'Gaming & Streaming',
     'Jugabilidad fluida y transmision en vivo sin perder fotogramas.',
     'Rendimiento enfocado en placa de video', 1),
    ('DISENO_EDICION', 'Diseno Grafico y Edicion de Video',
     'Crea, renderiza y edita proyectos visuales de alta complejidad.',
     'Potencia creativa', 2),
    ('OFICINA_HOGAR', 'Oficina y uso hogareno',
     'Tareas diarias, navegacion y multitarea con velocidad confiable.',
     'Esenciales del dia a dia', 3)
ON CONFLICT (codigo) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    texto_destacado = EXCLUDED.texto_destacado,
    orden_visual = EXCLUDED.orden_visual,
    activo = TRUE;

-- B. Categorias necesarias por perfil.
INSERT INTO perfil_tipos_componente
    (id_perfil, id_tipo, obligatorio, prioridad, cantidad_sugerida)
SELECT p.id_perfil, t.id_tipo, x.obligatorio, x.prioridad, x.cantidad
FROM (VALUES
    ('GAMING_STREAMING','CPU',TRUE,5,1),
    ('GAMING_STREAMING','CPU_COOLER',FALSE,3,1),
    ('GAMING_STREAMING','MOTHERBOARD',TRUE,5,1),
    ('GAMING_STREAMING','RAM',TRUE,4,1),
    ('GAMING_STREAMING','STORAGE',TRUE,4,1),
    ('GAMING_STREAMING','GPU',TRUE,5,1),
    ('GAMING_STREAMING','PSU',TRUE,5,1),
    ('GAMING_STREAMING','CASE',TRUE,3,1),
    ('DISENO_EDICION','CPU',TRUE,5,1),
    ('DISENO_EDICION','CPU_COOLER',FALSE,4,1),
    ('DISENO_EDICION','MOTHERBOARD',TRUE,5,1),
    ('DISENO_EDICION','RAM',TRUE,5,1),
    ('DISENO_EDICION','STORAGE',TRUE,5,1),
    ('DISENO_EDICION','GPU',TRUE,5,1),
    ('DISENO_EDICION','PSU',TRUE,4,1),
    ('DISENO_EDICION','CASE',TRUE,3,1),
    ('OFICINA_HOGAR','CPU',TRUE,5,1),
    ('OFICINA_HOGAR','MOTHERBOARD',TRUE,5,1),
    ('OFICINA_HOGAR','RAM',TRUE,4,1),
    ('OFICINA_HOGAR','STORAGE',TRUE,4,1),
    ('OFICINA_HOGAR','GPU',FALSE,1,1),
    ('OFICINA_HOGAR','PSU',TRUE,3,1),
    ('OFICINA_HOGAR','CASE',TRUE,3,1)
) AS x(codigo_perfil, codigo_tipo, obligatorio, prioridad, cantidad)
JOIN perfiles_uso p ON p.codigo = x.codigo_perfil
JOIN tipos_componente t ON t.nombre = x.codigo_tipo
ON CONFLICT (id_perfil, id_tipo) DO UPDATE SET
    obligatorio = EXCLUDED.obligatorio,
    prioridad = EXCLUDED.prioridad,
    cantidad_sugerida = EXCLUDED.cantidad_sugerida;

-- C. Reglas iniciales de afinidad basadas en el catalogo actual.
-- No usa IDs fijos: identifica productos mediante categoria y modelo.
INSERT INTO perfil_componentes
    (id_perfil, id_componente, afinidad, recomendado, observacion)
SELECT p.id_perfil, c.id_componente,
       CASE
         WHEN p.codigo = 'GAMING_STREAMING' AND t.nombre = 'GPU' THEN
              CASE WHEN c.modelo ILIKE '%4070%' THEN 5 WHEN c.modelo ILIKE '%4060%' THEN 4 ELSE 3 END
         WHEN p.codigo = 'DISENO_EDICION' AND t.nombre = 'RAM' THEN
              CASE WHEN (c.especificaciones->>'capacidad_gb')::int >= 64 THEN 5 ELSE 3 END
         WHEN p.codigo = 'DISENO_EDICION' AND t.nombre = 'GPU' THEN
              CASE WHEN COALESCE((c.especificaciones->>'vram_gb')::int,0) >= 12 THEN 5 ELSE 3 END
         WHEN p.codigo = 'OFICINA_HOGAR' AND t.nombre = 'GPU' THEN 1
         WHEN p.codigo = 'OFICINA_HOGAR' AND t.nombre = 'CPU' AND c.modelo IN ('7600','14600K') THEN 5
         ELSE 4
       END AS afinidad,
       CASE
         WHEN p.codigo = 'OFICINA_HOGAR' AND t.nombre = 'GPU' THEN FALSE
         ELSE TRUE
       END AS recomendado,
       CASE
         WHEN p.codigo = 'OFICINA_HOGAR' AND t.nombre = 'GPU'
           THEN 'Opcional: los procesadores cargados poseen grafica integrada.'
         ELSE NULL
       END
FROM perfiles_uso p
JOIN perfil_tipos_componente pt ON pt.id_perfil = p.id_perfil
JOIN tipos_componente t ON t.id_tipo = pt.id_tipo
JOIN componentes c ON c.id_tipo = t.id_tipo AND c.activo = TRUE
ON CONFLICT (id_perfil, id_componente) DO UPDATE SET
    afinidad = EXCLUDED.afinidad,
    recomendado = EXCLUDED.recomendado,
    observacion = EXCLUDED.observacion;

	

-- Inserto datos en la tabla tiendas
INSERT INTO tiendas (
    nombre,
    sitio_web,
    activo
)
VALUES
(
    'Mercado Libre',
    'https://www.mercadolibre.com.ar',
    TRUE
),
(
    'Compra Gamer',
    'https://compragamer.com',
    TRUE
),
(
    'Maximus Gaming',
    'https://www.maximus.com.ar',
    TRUE
),
(
    'FullH4rd',
    'https://www.fullh4rd.com.ar',
    TRUE
),
(
    'Mexx',
    'https://www.mexx.com.ar',
    TRUE
);


-- Inserto los precios de componentes segun las tiendas
INSERT INTO precios_componentes
(id_componente, id_tienda, precio, moneda, disponible)
VALUES

-- CPUs
(1, 1, 279999, 'ARS', TRUE),
(1, 2, 274999, 'ARS', TRUE),

(2, 1, 359999, 'ARS', TRUE),
(2, 3, 354999, 'ARS', TRUE),

(3, 2, 299999, 'ARS', TRUE),
(3, 4, 304999, 'ARS', TRUE),

(4, 1, 399999, 'ARS', TRUE),
(4, 5, 394999, 'ARS', TRUE),

-- SSDs
(17, 1, 119999, 'ARS', TRUE),
(17, 2, 114999, 'ARS', TRUE),

(18, 3, 112999, 'ARS', TRUE),
(18, 4, 116999, 'ARS', TRUE),

-- GPUs
(21, 1, 449999, 'ARS', TRUE),
(21, 2, 439999, 'ARS', TRUE),

(22, 2, 849999, 'ARS', TRUE),
(22, 3, 839999, 'ARS', TRUE),

(23, 1, 1599999, 'ARS', TRUE),
(23, 5, 1579999, 'ARS', TRUE),

(24, 1, 2499999, 'ARS', TRUE),
(24, 2, 2459999, 'ARS', TRUE),

-- PSUs
(25, 2, 119999, 'ARS', TRUE),
(26, 3, 149999, 'ARS', TRUE),
(27, 1, 189999, 'ARS', TRUE),
(28, 5, 249999, 'ARS', TRUE);
