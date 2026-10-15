# TP Final POO 3 - PC Builder Database
 
Sistema de gestión y configuración de PCs desarrollado en PostgreSQL.


## Descripción
 
Este proyecto implementa una base de datos relacional para un sistema de armado de computadoras.
 
Permite:
 
- Gestionar usuarios.
- Administrar componentes de hardware.
- Crear configuraciones de PC.
- Validar compatibilidades.
- Calcular precios y consumo energético.
- Gestionar stock.

---------------

## Objetivo

El objetivo del sistema es permitir a los usuarios crear configuraciones personalizadas de 
computadoras seleccionando componentes compatibles entre sí.

---------------

## Tecnologías

- PostgreSQL
- SQL
- PL/pgSQL

---------------

## Estructura

| Archivo | Descripción |
|----------|------------|
| 01_create_database.sql | Creación de la base de datos |
| 02_create_tables.sql | Creación de tablas |
| 03_insert_test_data.sql | Datos de prueba |
| 04_views.sql | Vistas |
| 05_functions.sql | Funciones |
| 06_procedures.sql | Procedimientos almacenados |
| 07_triggers.sql | Triggers |
| 08_test_queries.sql | Pruebas del sistema |

---------------

## Instalación

Ejecutar los scripts en el siguiente orden:

1. 01_create_database.sql
2. 02_create_tables.sql
3. 03_insert_test_data.sql
4. 04_views.sql
5. 05_functions.sql
6. 06_procedures.sql
7. 07_triggers.sql
8. 08_test_queries.sql

---------------

## Tablas principales

- usuarios
- marcas
- tipos_componente
- componentes
- configuraciones_pc
- configuracion_componentes
- reglas_compatibilidad
- resultados_compatibilidad
- tiendas
- precios_componentes

---------------

## Funcionalidades

### Funciones

- Calcular precio total de una configuración.
- Calcular consumo energético.
- Obtener stock disponible.
- Contar componentes.

### Procedures

- Crear configuración.
- Agregar componentes.
- Eliminar componentes.
- Finalizar configuración.

### Triggers

- Actualización automática de precio total.
- Actualización de fecha de modificación.
- Validación de stock.

---------------

## Integrantes
 
Grupo 7
 
- Almada Gonzalo
- Gonzalez Sofía
- Guillen Federico Nicolás
- Morilla Lucas
- Ortega Yazmín
