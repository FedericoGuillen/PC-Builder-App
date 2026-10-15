/*
===========================================================
Proyecto: TP Final POO_3, Grupo 7.
Archivo: 02_create_tables.sql
Descripción: Creación de las tablas de la base de datos, hay algunas que son opcionales (9 y 10).
===========================================================
*/

--1) Creo la tabla "usuarios": guarda a las personas que utilizan el sistema.
CREATE TABLE usuarios (
id_usuario BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
nombre VARCHAR(100) NOT NULL,
apellido VARCHAR(100),
email VARCHAR(255) NOT NULL UNIQUE,
password_hash TEXT NOT NULL,
fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
activo BOOLEAN NOT NULL DEFAULT TRUE
);

--2) Creo la tabla "marcas": permite evitar repetir nombres como AMD, Intel, NVIDIA, ASUS o Kingston en cada componente.
CREATE TABLE marcas (
id_marca BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
nombre VARCHAR(100) NOT NULL UNIQUE,
sitio_web TEXT,
activo BOOLEAN NOT NULL DEFAULT TRUE
);

--3) Creo la tabla "tipos_componente" : representa las categorías de componentes disponibles.
CREATE TABLE tipos_componente (
id_tipo BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
nombre VARCHAR(100) NOT NULL UNIQUE,
descripcion TEXT,
cantidad_maxima_sugerida INTEGER NOT NULL DEFAULT 1,
obligatorio BOOLEAN NOT NULL DEFAULT FALSE
);


--4) Creo la tabla "componentes": esta sería la tabla central del catálogo.
CREATE TABLE componentes (
id_componente BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
id_tipo BIGINT NOT NULL,
id_marca BIGINT NOT NULL,
nombre VARCHAR(200) NOT NULL,
modelo VARCHAR(150),
descripcion TEXT,
consumo_watts INTEGER,
precio_referencia NUMERIC(12, 2),
stock INTEGER NOT NULL DEFAULT 0,
especificaciones JSONB NOT NULL DEFAULT '{}'::JSONB,
imagen_url TEXT,
activo BOOLEAN NOT NULL DEFAULT TRUE,
fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_componente_tipo
FOREIGN KEY (id_tipo)
REFERENCES tipos_componente(id_tipo),

CONSTRAINT fk_componente_marca
FOREIGN KEY (id_marca)
REFERENCES marcas(id_marca),

CONSTRAINT chk_consumo_positivo
CHECK (consumo_watts IS NULL OR consumo_watts >= 0),

CONSTRAINT chk_precio_positivo
CHECK (precio_referencia IS NULL OR precio_referencia >= 0),

CONSTRAINT chk_stock_positivo
CHECK (stock >= 0)
);


--5) Creo la tabla "configuraciones_pc": esta tabla representa cada PC creada por un usuario.

CREATE TABLE configuraciones_pc (
id_configuracion BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
id_usuario BIGINT NOT NULL,
nombre VARCHAR(150) NOT NULL,
descripcion TEXT,
estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
precio_total NUMERIC(12, 2) NOT NULL DEFAULT 0,
es_publica BOOLEAN NOT NULL DEFAULT FALSE,
fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_configuracion_usuario
FOREIGN KEY (id_usuario)
REFERENCES usuarios(id_usuario)
ON DELETE CASCADE,

CONSTRAINT chk_estado_configuracion
CHECK (estado IN (
'BORRADOR',
'COMPLETA',
'INCOMPATIBLE',
'FINALIZADA'
)),

CONSTRAINT chk_precio_total
CHECK (precio_total >= 0)
);


--6) Creo la tabla "configuracion_componentes": esta tabla vincula las configuraciones con los componentes.
CREATE TABLE configuracion_componentes (
    id_configuracion_componente BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_configuracion BIGINT NOT NULL,
    id_componente BIGINT NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_al_seleccionar NUMERIC(12, 2) NOT NULL,
    posicion_x NUMERIC(10, 2),
    posicion_y NUMERIC(10, 2),
    rotacion NUMERIC(6, 2) NOT NULL DEFAULT 0,
    fecha_agregado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cc_configuracion
        FOREIGN KEY (id_configuracion)
        REFERENCES configuraciones_pc(id_configuracion)
        ON DELETE CASCADE,

    CONSTRAINT fk_cc_componente
        FOREIGN KEY (id_componente)
        REFERENCES componentes(id_componente),

    CONSTRAINT uq_configuracion_componente
        UNIQUE (id_configuracion, id_componente),

    CONSTRAINT chk_cantidad_positiva
        CHECK (cantidad > 0),

    CONSTRAINT chk_precio_seleccion
        CHECK (precio_al_seleccionar >= 0)
);


--/) Creo la tabla "reglas_compatibilidad": es una solución más escalable. En lugar de comparar productos específicos, comparan sus características.
CREATE TABLE reglas_compatibilidad (
id_regla BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
nombre VARCHAR(150) NOT NULL,
descripcion TEXT NOT NULL,
codigo VARCHAR(100) NOT NULL UNIQUE,
nivel VARCHAR(20) NOT NULL DEFAULT 'ERROR',
activa BOOLEAN NOT NULL DEFAULT TRUE,

CONSTRAINT chk_nivel_regla
CHECK (nivel IN ('INFO', 'ADVERTENCIA', 'ERROR'))
);


--8) Creo la tabla "resultados_compatibilidad": esta tabla permite mostrarle al usuario los problemas detectados.
CREATE TABLE resultados_compatibilidad (
id_resultado BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
id_configuracion BIGINT NOT NULL,
id_regla BIGINT NOT NULL,
resultado VARCHAR(20) NOT NULL,
mensaje TEXT NOT NULL,
fecha_validacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_resultado_configuracion
FOREIGN KEY (id_configuracion)
REFERENCES configuraciones_pc(id_configuracion)
ON DELETE CASCADE,

CONSTRAINT fk_resultado_regla
FOREIGN KEY (id_regla)
REFERENCES reglas_compatibilidad(id_regla),

CONSTRAINT chk_resultado
CHECK (resultado IN (
'COMPATIBLE',
'ADVERTENCIA',
'INCOMPATIBLE'
))
);


---- CONVIENE CREAR SOLO HASTA LA NUMERO 8, resultados_compatibilidad, para no complicar demasiado al proyecto.

--9) Creo la tabla "tiendas": para almacenar precios de distintas tiendas.
CREATE TABLE tiendas (
id_tienda BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
nombre VARCHAR(150) NOT NULL UNIQUE,
sitio_web TEXT,
activo BOOLEAN NOT NULL DEFAULT TRUE
);


--10) Creo la tabla precios_componentes: esto nos permite comparar tiendas, mostrar disponibilidad, encontrar el precio mas bajo
-- guardar precios historicos, calcular el total de una configuracion.
CREATE TABLE precios_componentes (
id_precio BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
id_componente BIGINT NOT NULL,
id_tienda BIGINT NOT NULL,
precio NUMERIC(12, 2) NOT NULL,
moneda CHAR(3) NOT NULL DEFAULT 'ARS',
url_producto TEXT,
disponible BOOLEAN NOT NULL DEFAULT TRUE,
fecha_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_precio_componente
FOREIGN KEY (id_componente)
REFERENCES componentes(id_componente)
ON DELETE CASCADE,

CONSTRAINT fk_precio_tienda
FOREIGN KEY (id_tienda)
REFERENCES tiendas(id_tienda),

CONSTRAINT chk_precio
CHECK (precio >= 0)
);