-- script para crear las tablas de la bd mineria_untrm

-- 1) Staging: copia fiel del CSV, todo texto
CREATE TABLE IF NOT EXISTS stg_ilpd (age TEXT, gender TEXT, tb TEXT, db TEXT, alkphos TEXT,
    sgpt TEXT, sgot TEXT, tp TEXT, alb TEXT, ag_ratio TEXT, dataset TEXT);

CREATE TABLE IF NOT EXISTS stg_lpd (LIKE stg_ilpd INCLUDING ALL);

-- 2) Tablas limpias (mismo esquema para las dos)
CREATE TABLE IF NOT EXISTS tabla_enfermedades (
    edad INT, genero CHAR(1), bilirrubina_total NUMERIC(6,2), bilirrubina_directa NUMERIC(6,2),
    fosfatasa_alcalina NUMERIC(8,1), alt_sgpt NUMERIC(8,1), ast_sgot NUMERIC(8,1),
    proteinas_totales NUMERIC(5,2), albumina NUMERIC(5,2), relacion_a_g NUMERIC(5,2),
    diagnostico SMALLINT CHECK (diagnostico IN (0,1)));

CREATE TABLE IF NOT EXISTS tabla_enfermedades_1 (LIKE tabla_enfermedades INCLUDING ALL);

-- 3) Integrada (union sin repetidos) y comunes
CREATE TABLE IF NOT EXISTS tabla_enfermedades_integrada (
    id_paciente SERIAL PRIMARY KEY, LIKE tabla_enfermedades INCLUDING ALL, origen VARCHAR(5));

CREATE TABLE IF NOT EXISTS tabla_comunes (LIKE tabla_enfermedades INCLUDING ALL);
