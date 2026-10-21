/*
===========================================================
Proyecto: TP Final POO_3, Grupo 7.
Archivo: 09_indexes.sql
Descripción: Creacion de índices.
===========================================================
*/



CREATE INDEX IF NOT EXISTS idx_componentes_tipo_activo
    ON componentes (id_tipo, activo);
CREATE INDEX IF NOT EXISTS idx_componentes_precio
    ON componentes (precio_referencia);
CREATE INDEX IF NOT EXISTS idx_componentes_especificaciones_gin
    ON componentes USING GIN (especificaciones);
CREATE INDEX IF NOT EXISTS idx_perfil_componentes_perfil_afinidad
    ON perfil_componentes (id_perfil, recomendado, afinidad DESC);