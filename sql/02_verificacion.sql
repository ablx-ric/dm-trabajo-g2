-- Consultas de verificacion

-- A) Conteos: Pentaho (sin sufijo) vs Python (_py). Esperado: 570 / 18539 / 18554 / 555
SELECT 'tabla_enfermedades' AS tabla, COUNT(*) AS filas FROM tabla_enfermedades
UNION ALL SELECT 'tabla_enfermedades_1', COUNT(*) FROM tabla_enfermedades_1
UNION ALL SELECT 'tabla_enfermedades_integrada', COUNT(*) FROM tabla_enfermedades_integrada
UNION ALL SELECT 'tabla_comunes', COUNT(*) FROM tabla_comunes
UNION ALL SELECT 'tabla_enfermedades_py', COUNT(*) FROM tabla_enfermedades_py
UNION ALL SELECT 'tabla_enfermedades_1_py', COUNT(*) FROM tabla_enfermedades_1_py
UNION ALL SELECT 'tabla_enfermedades_integrada_py', COUNT(*) FROM tabla_enfermedades_integrada_py
UNION ALL SELECT 'tabla_comunes_prediccion', COUNT(*) FROM tabla_comunes_prediccion;

-- B) Distribucion del diagnostico en la tabla integrada (Python)
SELECT diagnostico, COUNT(*) AS n,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM tabla_enfermedades_integrada_py
GROUP BY diagnostico ORDER BY diagnostico;

-- C) Acierto de los dos modelos sobre los registros comunes
SELECT ROUND(AVG(acierto_ilpd)::numeric, 3)       AS acierto_modelo_ilpd,
       ROUND(AVG(acierto_integrado)::numeric, 3)  AS acierto_modelo_integrado
FROM tabla_comunes_prediccion;

-- D) PDI vs Python: filas del dataset 1 que difieren entre ambos flujos (esperado: 0)
(SELECT edad, genero, bilirrubina_total::float, bilirrubina_directa::float, fosfatasa_alcalina::float,
        alt_sgpt::float, ast_sgot::float, proteinas_totales::float, albumina::float,
        relacion_a_g::float, diagnostico::int FROM tabla_enfermedades
 EXCEPT
 SELECT edad, genero, bilirrubina_total, bilirrubina_directa, fosfatasa_alcalina,
        alt_sgpt, ast_sgot, proteinas_totales, albumina, relacion_a_g, diagnostico FROM tabla_enfermedades_py);
