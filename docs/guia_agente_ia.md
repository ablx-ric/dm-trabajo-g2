# Guía de contexto para agentes de IA: Trabajo de Minería de Datos I (Grupo 2)

Este archivo da a un asistente de IA (Claude, Copilot, ChatGPT, etc.) todo el contexto del proyecto, para que ayude a cualquier integrante del grupo sin tener que reconstruir lo que ya se hizo. Léelo completo antes de proponer cambios.

- **Curso:** Minería de Datos I, Universidad Nacional Toribio Rodríguez de Mendoza de Amazonas (UNTRM).
- **Guía oficial de la práctica:** `docs/ETL_GRUPO2.docx` (la original del docente es `docs/Practica_ETL_Pentaho_PostgreSQL_Python_UNTRM.docx`; el contenido es el mismo).
- **Fuente de los datos:** `docs/Dataset.txt` (Kaggle, *Liver Disease Patient Dataset*).

---

## 1. De qué trata el trabajo

Hay que diseñar e implementar un **proceso ETL** que integre dos datasets clínicos de **enfermedad hepática** y deje los datos listos para un modelo predictivo. Se usan tres herramientas:

- **Pentaho Data Integration (PDI / Spoon):** transformaciones y job ETL. Es la parte principal.
- **PostgreSQL:** almacén de datos. Se administra con DBeaver o pgAdmin.
- **Python:** el mismo ETL hecho en código, más un modelo de clasificación cuyas predicciones se guardan en PostgreSQL.

El título original de la práctica menciona enfermedad renal crónica, pero los CSV entregados son de enfermedad **hepática**. La guía lo aclara y pide trabajar con estos datos. La pregunta 5 del informe pide explicar qué cambiaría con un dataset renal.

### Entregables y peso

| N.º | Entregable | Peso |
|---|---|---|
| 1 | `t1_ilpd.ktr`, `t2_lpd.ktr`, `t3_integracion.ktr` y `job_etl.kjb` | 30 % |
| 2 | Capturas de cada actividad (1 a 8) con el Preview de datos | 20 % |
| 3 | `etl_modelo.py` funcionando y las tablas en PostgreSQL | 25 % |
| 4 | Informe: decisiones de limpieza, comparación PDI vs Python y análisis del modelo | 25 % |

### Preguntas que debe responder el informe

1. ¿Cuántos registros se eliminaron en cada paso y por qué es válido eliminarlos?
2. ¿Por qué la mediana es preferible a la media para imputar enzimas hepáticas?
3. ¿Qué diferencias de resultado hay entre PDI y Python en las filas finales? Justificarlas.
4. ¿Por qué el modelo A obtiene ~99,7 % y el modelo B solo ~69-71 %? ¿Cuál se usaría en un entorno clínico?
5. ¿Qué cambios requeriría este flujo para trabajar con un dataset de enfermedad renal crónica?

---

## 2. Entorno de trabajo (Windows 10/11)

| Herramienta | Versión / detalle |
|---|---|
| Pentaho Data Integration | 11.0 (Spoon, se abre con `Spoon.bat`) |
| Java | Temurin JDK 21. PDI 11 lo soporta. |
| Driver JDBC | `postgresql-42.7.11.jar` en `data-integration\lib`. Debe haber **un solo** jar de PostgreSQL ahí. |
| PostgreSQL | 18, en `localhost:5432`, usuario `postgres` |
| Cliente SQL | DBeaver/pgAdmin |
| Python | 3.10, gestionado con **uv** |
| Terminal | Nushell (también sirve PowerShell) |

### Problemas ya resueltos (no repetir el diagnóstico)

- **DBeaver no entiende `\c`** (es exclusivo de `psql`). La base se crea aparte y luego se ejecuta el script conectado a ella.

---

## 3. Estructura del repositorio

```
dm-trabajo-g2/
├── data/
│   ├── indian_liver_patient.csv                 # Dataset 1 (ILPD)
│   └── Liver_Patient_Dataset__LPD__train.csv    # Dataset 2 (LPD), renombrado desde "Liver Patient Dataset (LPD)_train.csv"
├── docs/
│   ├── ETL_GRUPO2.docx                          # Guía de la práctica (referencia principal)
│   ├── Practica_ETL_Pentaho_PostgreSQL_Python_UNTRM.docx   # Guía original del docente
│   ├── Dataset.txt                              # Enlace a Kaggle
│   ├── guia_agente_ia.md                        # Este archivo
│   └── referencia/                              # PDFs de contexto (no son parte del entregable)
├── pentaho/                                     # Transformaciones .ktr y job .kjb
├── sql/
│   ├── 01_crear_tablas.sql                      # Tablas para el flujo de Pentaho
│   └── 02_verificacion.sql                      # Conteos y comparaciones para el informe
├── src/dm_trabajo_g2/__init__.py                # Lo creó `uv init`. No se usa, pero no se borra (pyproject lo referencia).
├── _descartar/                                  # Archivos que no se usan (notebooks PyCaret/Streamlit, test.csv.xlsx, script duplicado)
├── etl_modelo.py                                # ETL + modelo en Python
├── pyproject.toml, uv.lock, .python-version     # Proyecto uv (Python 3.10)
└── README.md
```

`_descartar/` contiene material de otro enfoque (PyCaret y Streamlit). La guía ETL no lo pide. No lo uses salvo que el docente confirme que esa parte también se evalúa.

---

## 4. Los datos

| Característica | Dataset 1: ILPD | Dataset 2: LPD |
|---|---|---|
| Archivo | `data/indian_liver_patient.csv` | `data/Liver_Patient_Dataset__LPD__train.csv` |
| Filas originales | 583 | 30 691 |
| Columnas | 11 (10 variables + clase) | 11 (10 variables + clase) |
| Codificación | UTF-8 | **ISO-8859-1 (latin1)**, fin de línea CRLF |
| Clase | `Dataset` (1 = enfermo, 2 = sano) | `Result` (1 = enfermo, 2 = sano) |
| Celdas nulas | 4 (solo relación A/G) | 5 425 en 3 533 filas |
| Filas tras quitar nulos críticos | 583 | 29 787 (se descartan 904 sin edad o género) |
| Duplicados | 13 | 11 248 |
| Filas finales | **570** | **18 539** |

**Detalle que rompe flujos:** en el dataset 2 varios encabezados empiezan con un espacio no separable (por ejemplo `" Alkphos Alkaline Phosphotase"`), y los nombres son largos (`Age of the patient`, `Gender of the patient`, `A/G Ratio Albumin and Globulin Ratio`...). En PDI hay que usar **Get Fields** y renombrar desde la lista, nunca escribir los nombres a mano. En Python se renombra por posición.

### Esquema unificado (igual para ambos datasets)

| Nombre unificado | Dataset 1 | Dataset 2 | Tipo |
|---|---|---|---|
| edad | Age | Age of the patient | Integer |
| genero | Gender | Gender of the patient | String(1): M/F |
| bilirrubina_total | Total_Bilirubin | Total Bilirubin | Number |
| bilirrubina_directa | Direct_Bilirubin | Direct Bilirubin | Number |
| fosfatasa_alcalina | Alkaline_Phosphotase | Alkphos ... | Number |
| alt_sgpt | Alamine_Aminotransferase | Sgpt ... | Number |
| ast_sgot | Aspartate_Aminotransferase | Sgot ... | Number |
| proteinas_totales | Total_Protiens | Total Protiens | Number |
| albumina | Albumin | ALB Albumin | Number |
| relacion_a_g | Albumin_and_Globulin_Ratio | A/G Ratio ... | Number |
| diagnostico | Dataset | Result | Integer: 1 = enfermo, 0 = sano |

---

## 5. Arquitectura del proceso

Flujo: CSV → staging en PostgreSQL → limpieza en PDI → tablas limpias → integración → tabla de comunes → modelo en Python → tabla con predicciones.

| Paso | Archivo | Entrada | Salida en PostgreSQL |
|---|---|---|---|
| T1 | `pentaho/t1_ilpd.ktr` | `indian_liver_patient.csv` | `stg_ilpd` y `tabla_enfermedades` |
| T2 | `pentaho/t2_lpd.ktr` | `Liver_Patient_Dataset__LPD__train.csv` | `stg_lpd` y `tabla_enfermedades_1` |
| T3 | `pentaho/t3_integracion.ktr` | `tabla_enfermedades` y `tabla_enfermedades_1` | `tabla_enfermedades_integrada` y `tabla_comunes` |
| JOB | `pentaho/job_etl.kjb` | T1 → T2 → T3 | Todas las anteriores |
| PY | `etl_modelo.py` | Los CSV de `data/` | Tablas `_py` y `tabla_comunes_prediccion` |

### Tablas en la base `mineria_untrm`

**Llenadas por Pentaho** (las crea `sql/01_crear_tablas.sql`):

| Tabla | Filas esperadas | Contenido |
|---|---|---|
| `stg_ilpd` | 583 | Copia fiel del CSV 1, todo texto |
| `stg_lpd` | 30 691 | Copia fiel del CSV 2, todo texto |
| `tabla_enfermedades` | 570 | Dataset 1 limpio |
| `tabla_enfermedades_1` | 18 539 | Dataset 2 limpio |
| `tabla_enfermedades_integrada` | 18 554 | Unión sin duplicados (570 + 18 539 − 555), con `id_paciente` y `origen` |
| `tabla_comunes` | 555 | Registros idénticos en ambos datasets |

**Llenadas por Python** (las crea el propio script):

| Tabla | Filas |
|---|---|
| `tabla_enfermedades_py` | 570 |
| `tabla_enfermedades_1_py` | 18 539 |
| `tabla_enfermedades_integrada_py` | 18 554 |
| `tabla_comunes_prediccion` | 555 |

**Decisión del grupo:** el script de Python escribe en tablas con sufijo `_py` para **no sobrescribir** las de Pentaho. Así se pueden comparar ambos flujos (pregunta 3). El sufijo se controla con la variable de entorno `SUFIJO_TABLAS`; vacía, el script escribe en los nombres originales. **No cambiar esto sin acordarlo con el grupo.**

---

## 6. Estado actual del trabajo

### Hecho

- [x] Carpeta organizada y proyecto uv creado (Python 3.10; dependencias: pandas, numpy, scikit-learn, sqlalchemy, psycopg2-binary).
- [x] Base `mineria_untrm` creada y `sql/01_crear_tablas.sql` ejecutado.
- [x] `etl_modelo.py` corregido y ejecutado con éxito. Las 4 tablas de Python están cargadas.
- [x] Pentaho funcionando (se corrigió `PENTAHO_JAVA_HOME`) y conexión `conection-mineria-untrm-bd` creada y probada. Es global (en *View → Configurations → Database connections*), así que sirve para T1, T2 y T3 sin hacer Share.
- [x] **T1, actividad 1:** CSV file input → Table output (`stg_ilpd`). Ejecutado: 583 filas escritas y 0 errores. Verificado en DBeaver.

### En curso

- [ ] **T1, actividad 2:** Select values para renombrar al esquema unificado.

### Pendiente

- [ ] T1: actividades 3 a 6 y Table output a `tabla_enfermedades` (actividad 8).
- [ ] T2: copia de T1 adaptada al dataset 2.
- [ ] T3: integración y comunes.
- [ ] `job_etl.kjb`.
- [ ] Ejecutar `sql/02_verificacion.sql` completo (las consultas A y D necesitan las tablas de Pentaho llenas).
- [ ] Capturas de las actividades restantes.
- [ ] Informe: llenar la carátula y responder las 5 preguntas.

---

## 7. Detalle de las transformaciones en Pentaho

**Convenciones del proyecto:**

- Los `.ktr` y `.kjb` se guardan en `pentaho/`. **Guarda la transformación antes de configurar rutas**, porque la variable `${Internal.Entry.Current.Directory}` solo tiene valor si el archivo está guardado.
- Las rutas a los CSV son relativas: `${Internal.Entry.Current.Directory}/../data/<archivo>.csv`. No uses rutas absolutas como `D:/...`, porque no funcionan en el equipo de otro integrante.
- Para conectar pasos: Shift y arrastrar, y elegir **Main output of step**. Cuando un paso tiene dos salidas, elegir **Copy data to next steps**, para no repartir las filas entre ramas.
- Haz **Preview** después de cada paso y toma la captura para el informe.
- Conexión a usar en todos los pasos de base de datos: `conection-mineria-untrm-bd`, esquema `public`.

### T1 (`t1_ilpd.ktr`), dataset 1

| # | Paso (actividad) | Configuración | Estado |
|---|---|---|---|
| 1 | **CSV file input** (1) | Ruta `${Internal.Entry.Current.Directory}/../data/indian_liver_patient.csv`. Delimitador `,`, enclosure `"`, Lazy conversion **desactivado**, Header row activado, encoding UTF-8. Get Fields y los 11 campos como **String**, sin format, length ni precision. | Hecho |
| 2 | **Table output** → `stg_ilpd` (1) | Truncate table, commit 1000, batch update. **Specify database fields** activado y mapeo: Age→age, Gender→gender, Total_Bilirubin→tb, Direct_Bilirubin→db, Alkaline_Phosphotase→alkphos, Alamine_Aminotransferase→sgpt, Aspartate_Aminotransferase→sgot, Total_Protiens→tp, Albumin→alb, Albumin_and_Globulin_Ratio→ag_ratio, Dataset→dataset. No usar Guess, porque no acierta con las abreviaturas. | Hecho |
| 3 | **Select values** (2) | Segunda salida del CSV (Copy data to next steps). Pestaña Select & Alter: Get fields to select y Rename to según el esquema unificado (sección 4). No hay columna ID que eliminar. | En curso |
| 4 | **Replace in String** (3) | Todas las columnas: RegEx activado, buscar `^\s*$`, reemplazar por vacío. Convierte celdas con solo espacios en nulos. | Pendiente |
| 5 | **Filter rows** (3) | `genero IS NOT NULL AND edad IS NOT NULL`. No se imputan edad ni género, porque inventarlos distorsiona el análisis. | Pendiente |
| 6 | **If field value is null** (3) | Mediana por columna como constante. En el dataset 1 solo `relacion_a_g` = `0.93`. | Pendiente |
| 7 | **String operations** (4) | `genero`: Trim = both, Lower/Upper = lower. | Pendiente |
| 8 | **Value mapper** ×2 (4) | `genero`: male→M, female→F (sin coincidencia: vacío). `diagnostico`: 1→1, 2→0. | Pendiente |
| 9 | **Select values**, pestaña Meta-data (5) | `edad` y `diagnostico` a Integer (`#`). `bilirrubina_*`, `proteinas_totales`, `albumina` y `relacion_a_g` a Number (`#.##`). `fosfatasa_alcalina`, `alt_sgpt` y `ast_sgot` a Number (`#.#`). **Decimal symbol `.` y grouping vacío.** `genero` String de longitud 1. | Pendiente |
| 10 | **Sort rows** → **Unique rows** (6) | Ordenar por las 11 columnas, ascendente. Unique rows comparando las 11, con Add counter. Unique rows solo compara filas consecutivas, por eso hay que ordenar antes. | Pendiente |
| 11 | **Table output** → `tabla_enfermedades` (8) | Truncate, commit 1000, batch update. Los nombres ya coinciden, no hace falta mapear. | Pendiente |

**Resultado esperado de T1:** 583 filas en `stg_ilpd` y 570 en `tabla_enfermedades` (13 duplicados).

### T2 (`t2_lpd.ktr`), dataset 2

Crear con **File → Save as** desde T1 y cambiar:

1. CSV file input: archivo `Liver_Patient_Dataset__LPD__train.csv` y encoding **ISO-8859-1**. Repetir Get Fields, porque los nombres de columna son otros, y poner todo en String.
2. Table output de staging: tabla `stg_lpd` y rehacer el mapeo por posición (el orden de las columnas es el mismo que en el dataset 1).
3. Select values (renombrar): rehacer **Get fields to select**, porque los nombres de origen cambian (ojo con los espacios no separables).
4. If field value is null, con las medianas del dataset 2:

| Columna | Mediana dataset 2 |
|---|---|
| relacion_a_g | 0.90 |
| bilirrubina_total | 1.0 |
| bilirrubina_directa | 0.3 |
| fosfatasa_alcalina | 209 |
| alt_sgpt | 35 |
| ast_sgot | 42 |
| proteinas_totales | 6.6 |
| albumina | 3.1 |

5. Table output final: tabla `tabla_enfermedades_1`.

**Resultado esperado de T2:** 30 691 filas en `stg_lpd`, 29 787 tras Filter rows (904 descartadas) y 18 539 en `tabla_enfermedades_1`. Unique rows (HashSet) es opcional y más rápido para este dataset.

### T3 (`t3_integracion.ktr`), integración (actividad 7)

1. **Table input A:** `SELECT * FROM tabla_enfermedades`. **Table input B:** `SELECT * FROM tabla_enfermedades_1`.
2. **Add constants** en cada rama: `origen` = `ILPD` en A y `LPD` en B (String).
3. **Append streams:** Head hop = A, Tail hop = B. Ambas ramas deben tener exactamente los mismos campos y tipos.
4. **Sort rows** por todas las columnas excepto `origen`, y **Unique rows** con esas mismas columnas. Un registro presente en ambos datasets queda una sola vez, con origen ILPD.
5. **Add sequence:** campo `id_paciente`, valor inicial 1, incremento 1.
6. **Table output** → `tabla_enfermedades_integrada` (18 554 filas).
7. Rama paralela para los comunes: Sort rows de A y de B por las 11 columnas, **Merge join** con Join type = INNER y las 11 columnas como claves, y Table output → `tabla_comunes` (555 filas). Hay que quitar los campos duplicados que genera el join (con Select values) antes de cargar.

### Job (`job_etl.kjb`)

Start → T1 → T2 → T3 → Success. En cada hop usar **Follow when result is true**, para que el flujo se detenga si una transformación falla. Ejecutar y guardar capturas de **Logging** y **Step Metrics**.

### Actividad 8: Table output vs Insert/Update

- **Table output:** carga inicial completa, con Truncate activado. Se usa en todas las tablas.
- **Insert/Update:** recargas sin duplicar, sobre `tabla_enfermedades_integrada`. Compara por las 10 variables clínicas y actualiza solo `diagnostico`. Basta con explicarlo y, si se quiere, mostrarlo en una captura.

---

## 8. Flujo en Python (`etl_modelo.py`)

### Cómo ejecutarlo

Desde la raíz del proyecto:

```nu
# Nushell
$env.PG_URL = "postgresql+psycopg2://postgres:TU_CLAVE@localhost:5432/mineria_untrm"
uv run etl_modelo.py
```

```powershell
# PowerShell
$env:PG_URL = "postgresql+psycopg2://postgres:TU_CLAVE@localhost:5432/mineria_untrm"
uv run etl_modelo.py
```

**Nunca escribir la contraseña real en el código ni subirla al repositorio.** Va solo en la variable de entorno `PG_URL`. La base `mineria_untrm` debe existir antes; si no, sale el error `database "mineria_untrm" does not exist`.

### Qué hace

Cada bloque del script equivale a un paso de PDI (los comentarios lo indican):

1. Lee los dos CSV (prueba UTF-8 y luego latin1).
2. Limpia: renombra por posición, normaliza género, recodifica la clase (2→0), convierte tipos, descarta filas sin edad/género/diagnóstico, imputa la **mediana de cada dataset** y elimina duplicados.
3. Carga `tabla_enfermedades_py` y `tabla_enfermedades_1_py`.
4. Integra los datasets: une, marca los registros comunes, elimina duplicados (en los comunes gana ILPD) y agrega `id_paciente`. Carga `tabla_enfermedades_integrada_py`.
5. **Modelo A:** Random Forest (300 árboles, `class_weight="balanced"`, `random_state=42`) sobre el integrado, con prueba del 25 %.
6. **Comprobación de fuga:** entrena con LPD sin los comunes y prueba con ILPD.
7. **Modelo B:** solo dataset 1 (570 filas), validación cruzada estratificada de 5 particiones.
8. Probabilidades fuera de muestra (5-fold) para ambos modelos. Carga `tabla_comunes_prediccion` con `prob_modelo_integrado`, `pred_integrado`, `prob_modelo_ilpd`, `pred_ilpd`, `acierto_integrado` y `acierto_ilpd`.

Tarda unos 25 segundos.

### Resultados obtenidos (ejecución del grupo)

| Paso | Resultado |
|---|---|
| Dataset 1 | 583 → 583 → 570 (4 celdas nulas imputadas, 13 duplicados) |
| Dataset 2 | 30 691 → 29 787 → 18 539 (5 425 celdas nulas, 904 filas sin datos críticos) |
| Integrada | 18 554 filas, 555 comunes |
| Distribución integrada | 71,4 % enfermos (1), 28,6 % sanos (0) |

| Modelo | Exactitud | Precisión | Recall | F1 | AUC |
|---|---|---|---|---|---|
| A. Integrado (prueba 25 %) | 0,997 | 0,996 | 0,999 | 0,998 | 0,999 |
| B. Solo ILPD (CV 5-fold, n = 570) | 0,711 | — | 0,887 | — | 0,730 |

- Fuga (entrena LPD sin comunes, prueba ILPD): **exactitud 1,0**.
- Acierto sobre los 555 comunes: **1,0** con el modelo A y **0,71** con el B.
- Importancia de variables (modelo A): fosfatasa alcalina 0,159, AST 0,156, ALT 0,147, bilirrubina total 0,126, bilirrubina directa 0,112, albúmina 0,104, proteínas 0,102, relación A/G 0,088. Edad 0,004 y género 0,000 casi no aportan.

Las métricas del modelo B varían entre ejecuciones y equipos (AUC entre 0,71 y 0,74 según el orden de filas y la versión de scikit-learn), porque son solo 570 registros. **En el informe se citan los números de la ejecución propia, no los de la guía.**

---

## 9. Hallazgos clave para el informe

- **El modelo A está inflado.** Un 99,7 % de exactitud en datos clínicos de este tipo no es creíble. El dataset 2 contiene muchos registros casi idénticos entre sí (y versiones de los del dataset 1), lo que provoca fuga de información entre entrenamiento y prueba. La comprobación de fuga lo demuestra: entrenar con LPD y probar con ILPD da 100 %. Las métricas del modelo A reflejan memorización, no capacidad de generalizar.
- **El modelo B es la estimación realista** (AUC ~0,73, exactitud ~0,71). En un entorno clínico se usaría ese criterio de evaluación. Su recall alto (~0,89) es deseable, porque reduce los pacientes enfermos que pasan sin detectar.
- **Mediana vs media:** las enzimas (ALT, AST, fosfatasa alcalina) y las bilirrubinas tienen distribuciones muy sesgadas, con valores extremos. La mediana es robusta a esos extremos; la media se desplaza hacia ellos.
- **Eliminación de registros:** los duplicados exactos no aportan información y sesgan el modelo. Las filas sin edad o género se descartan en lugar de imputarse, porque inventar esos datos distorsionaría el análisis.
- **PDI vs Python:** deben coincidir en filas (570, 18 539, 18 554, 555). Diferencias posibles: PDI usa medianas fijas tomadas de la guía, mientras Python las calcula sobre los datos; el redondeo de los tipos NUMERIC de PostgreSQL frente a float64; y la forma de detectar los comunes. La consulta D de `sql/02_verificacion.sql` compara el dataset 1 entre ambos flujos (esperado: 0 filas diferentes).
- **Para enfermedad renal (pregunta 5):** el flujo es el mismo. Cambian los nombres de columnas, el esquema unificado, las reglas de limpieza (por ejemplo, el dataset CKD de UCI usa `?` como nulo y tiene variables categóricas como `htn` o `dm`), las medianas y los mapeos de categorías y de la clase (`ckd`/`notckd`).

---

## 10. Reglas para el agente de IA

1. **La referencia es `docs/ETL_GRUPO2.docx`.** Ante una duda sobre qué pide la práctica, sigue la guía. No inventes requisitos.
2. **No subas credenciales.** La contraseña de PostgreSQL va solo en `PG_URL`.
3. **No cambies los nombres de tablas** ni el sufijo `_py` sin acordarlo con el grupo. Las consultas de `sql/` dependen de ellos.
4. **Rutas relativas siempre:** `data/` en Python y `${Internal.Entry.Current.Directory}/../data/` en Pentaho.
5. **Antes de dar por buena una transformación, compara con los conteos esperados:** 583 / 570 (T1), 30 691 / 29 787 / 18 539 (T2), 18 554 / 555 (T3).
6. **Pentaho se configura en la interfaz gráfica.** Da instrucciones paso a paso y pide una captura o el log cuando haya un error. Si generas XML de `.ktr`, avisa que no está probado.
7. **Cada actividad necesita su captura de Preview** para el informe (20 % de la nota). Recuérdalo al terminar cada paso.
8. **Responde en español**, de forma breve y concreta.
9. **No uses `_descartar/`** ni PyCaret salvo que el grupo indique lo contrario.
