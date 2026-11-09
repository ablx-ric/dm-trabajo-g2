# Guía de contexto para agentes de IA: Trabajo de Minería de Datos I (Grupo 2)

Este archivo da a un asistente de IA (Claude, Copilot, ChatGPT, etc.) **todo el contexto del proyecto**, para que ayude a cualquier integrante del grupo sin reconstruir lo que ya se hizo y **sin cometer errores en Pentaho**. Léelo completo antes de proponer cambios. Las instrucciones de Pentaho de este archivo se probaron en T1 y funcionan; síguelas al pie de la letra.

- **Curso:** Minería de Datos I, Universidad Nacional Toribio Rodríguez de Mendoza de Amazonas (UNTRM).
- **Guía oficial de la práctica:** `docs/ETL_GRUPO2.docx` (la original del docente es `docs/Practica_ETL_Pentaho_PostgreSQL_Python_UNTRM.docx`; mismo contenido).
- **Fuente de los datos:** `docs/Dataset.txt` (Kaggle, *Liver Disease Patient Dataset*).

---

## 0. Reparto de tareas y estado (actualizar al terminar cada parte)

| Parte | Responsable | Estado |
|---|---|---|
| Organización del repo, proyecto uv, SQL y `etl_modelo.py` | Integrante 1 | **Hecho** |
| T1 `t1_ilpd.ktr` (dataset 1, completo) | Integrante 1 | **Hecho** (583 → 570 filas) |
| T2 `t2_lpd.ktr`: CSV file input y Staging stg_lpd | Integrante 1 | **Hecho** |
| T2 `t2_lpd.ktr`: desde **Renombrar campos** hasta el final | Integrante 2 | **Hecho** (30 691 → 18 539; E=0) |
| T3 `t3_integracion.ktr`: rama de integración (pasos 1 a 9) | Integrante 1 | **Hecho** (19 109 → 18 554; E=0) |
| T3 `t3_integracion.ktr`: rama de comunes (pasos 10 a 14) | Integrante 3 | **Hecho** (18 554 integrada, 555 comunes; E=0; revisado el `.ktr`) |
| Demostración Insert/Update (actividad 8, sección 9.5) | Por asignar | **Pendiente**: no está en `t3_integracion.ktr` |
| Job `job_etl.kjb` | Integrante 4 | **Pendiente, sigue ahora** (sección 10, rama `job-etl`) |
| Consultas de verificación y capturas finales | Todos | Pendiente (sección 11) |
| Informe (carátula y 5 preguntas) | Todos | Pendiente (sección 13) |

**Orden obligatorio:** T2 debe estar terminado antes de T3, porque T3 lee `tabla_enfermedades_1`. El job necesita T1, T2 y T3.

**Cada parte se trabaja en su propia rama de Git y se integra a `main` con un Pull Request** (ramas `t2-lpd`, `t3-integracion` y `job-etl`; detalle en la sección 3).

**Punto actual:** T1, T2 y T3 están **completos y fusionados en `main`** (T3: integración 18 554 + comunes 555, verificadas con Run y en DBeaver; hop duplicado Leer LPD → Origen LPD eliminado y revalidado). Sigue el Integrante 4 con el job (sección 10), creando la rama `job-etl` desde `main` actualizado. Queda pendiente aparte la demostración de Insert/Update (sección 9.5).

---

## 1. De qué trata el trabajo

Hay que diseñar e implementar un **proceso ETL** que integre dos datasets clínicos de **enfermedad hepática** y deje los datos listos para un modelo predictivo. Se usan tres herramientas:

- **Pentaho Data Integration (PDI / Spoon):** transformaciones y job ETL. Es la parte principal.
- **PostgreSQL:** almacén de datos. Se administra con DBeaver.
- **Python:** el mismo ETL hecho en código, más un modelo de clasificación cuyas predicciones se guardan en PostgreSQL.

El título original de la práctica menciona enfermedad renal crónica, pero los CSV son de enfermedad **hepática**. La guía lo aclara y pide trabajar con estos datos. La pregunta 5 del informe pide explicar qué cambiaría con un dataset renal.

### Entregables y peso

| N.º | Entregable | Peso |
|---|---|---|
| 1 | `t1_ilpd.ktr`, `t2_lpd.ktr`, `t3_integracion.ktr` y `job_etl.kjb` | 30 % |
| 2 | Capturas de cada actividad (1 a 8) con el Preview de datos | 20 % |
| 3 | `etl_modelo.py` funcionando y las tablas en PostgreSQL | 25 % |
| 4 | Informe: decisiones de limpieza, comparación PDI vs Python y análisis del modelo | 25 % |

### Las 8 actividades de la guía y dónde se hacen

| Actividad | Qué es | Dónde |
|---|---|---|
| 1 | Importar los CSV (y guardarlos en staging) | T1 y T2 |
| 2 | Eliminar identificadores y unificar nombres | T1 y T2 |
| 3 | Limpiar valores faltantes | T1 y T2 |
| 4 | Normalizar categorías | T1 y T2 |
| 5 | Convertir tipos de datos | T1 y T2 |
| 6 | Detectar y eliminar duplicados | T1 y T2 |
| 7 | Integrar los datasets | T3 |
| 8 | Cargar PostgreSQL (Table output, Insert/Update) | Final de T1, T2 y T3 |

---

## 2. Preparar tu computadora (cada integrante, antes de empezar)

Cada integrante trabaja en su propia PC con su propio PostgreSQL. Las tablas **no viajan por GitHub**: cada uno debe crearlas y llenarlas localmente.

| Herramienta | Versión usada por el grupo |
|---|---|
| Pentaho Data Integration | **11.0** (`Spoon.bat`). **Todos deben usar la 11**: con la 9.1 los `.ktr` del grupo fallan (ver tabla de problemas). |
| Java | Temurin JDK 21 (PDI 11 lo soporta) |
| Driver JDBC | `postgresql-42.7.x.jar` en `data-integration\lib` (**solo uno**) |
| PostgreSQL | 18, `localhost:5432`, usuario `postgres` |
| Cliente SQL | DBeaver |
| Python | 3.10 con **uv** |

### Pasos de preparación

1. **Clonar o actualizar el repo** (`git pull`).
2. **Driver JDBC:** copiar un `postgresql-42.x.jar` en `data-integration\lib`. Si DBeaver ya lo descargó, está en `%APPDATA%\DBeaverData\drivers\maven\maven-central\org.postgresql\`. Deja **un solo** jar de PostgreSQL en `lib`. Reinicia Spoon.
3. **Base de datos:** en DBeaver, clic derecho en la conexión PostgreSQL → **Create → Database** → `mineria_untrm`. Conéctate a **esa** base y ejecuta `sql/01_crear_tablas.sql` con **Alt+X** (ejecutar script). No uses `\c`: DBeaver no lo entiende.
4. **Conexión en Pentaho:** en el panel izquierdo, pestaña **View** → **Configurations → Database connections** → clic derecho → **New**:
   - **Connection name:** `conection-mineria-untrm-bd` (**escríbelo exactamente así, con la falta de ortografía "conection"**; las transformaciones buscan la conexión por ese nombre).
   - Tipo **PostgreSQL**, acceso **Native (JDBC)**, host `localhost`, base `mineria_untrm`, puerto `5432`, usuario `postgres` y tu contraseña.
   - Pulsa **Test** y luego **OK**. En PDI 11 estas conexiones son globales: no hace falta "Share".
5. **Llenar las tablas previas** según tu parte:
   - Integrante 2 (T2): no necesita nada previo.
   - Integrante 3 (T3): abrir y ejecutar (**Run**) `t1_ilpd.ktr` y `t2_lpd.ktr` para llenar `tabla_enfermedades` y `tabla_enfermedades_1`.
   - Integrante 4 (job): el propio job ejecuta todo.
6. **Python (opcional, para comparar):** desde la raíz del repo:

```powershell
uv sync
$env:PG_URL = "postgresql+psycopg2://postgres:TU_CLAVE@localhost:5432/mineria_untrm"
uv run etl_modelo.py
```

(En Nushell: `$env.PG_URL = "..."`.) **Nunca escribas tu contraseña en archivos del repo.**

### Problemas ya vistos y su solución

| Síntoma | Causa | Solución |
|---|---|---|
| Spoon no abre: "Windows cannot find ...jdk-21...\javaw.exe" | `PENTAHO_JAVA_HOME` apunta a un JDK que ya no existe (se actualizó Java) | Ver la carpeta real con `Get-ChildItem "C:\Program Files\Eclipse Adoptium"` y actualizar la variable: `[Environment]::SetEnvironmentVariable("PENTAHO_JAVA_HOME","C:\Program Files\Eclipse Adoptium\<carpeta-jdk>","User")`. Abrir una terminal nueva. |
| Error de driver al probar la conexión | Falta el jar o hay dos versiones | Un solo `postgresql-42.x.jar` en `lib` y reiniciar Spoon |
| `database "mineria_untrm" does not exist` | No se creó la base | Crearla en DBeaver (paso 3) |
| Valores como `0.9` se leen como `9` | Windows en español usa coma decimal | En Convertir tipos poner **Decimal = `.`** en cada campo Number |
| PDI 9.1: `NullPointerException at TableOutput.init` | La 9.1 no tiene conexiones globales: el `.ktr` solo guarda el nombre de la conexión y la 9.1 no la encuentra | Instalar **PDI 11** y crear la conexión global con el nombre exacto |
| `!BaseDatabaseStep.Init.ConnectionMissing!` en un Table output | Ese paso quedó sin conexión asignada (por ejemplo, el `.ktr` se abrió o guardó en otra versión) | `git restore pentaho/<archivo>.ktr`, volver a abrirlo en Spoon y ejecutar. Si persiste, elegir la conexión en el paso **sin hacer commit** y avisar al grupo |
| `no existe la relación «public.stg_ilpd»` (o cualquier tabla) | No se ejecutó `sql/01_crear_tablas.sql`, o se ejecutó en otra base, o la conexión apunta a otra base | En DBeaver, conectado a **`mineria_untrm`**, ejecutar `01_crear_tablas.sql` con Alt+X. Verificar que la conexión de Spoon tenga Database Name `mineria_untrm` |
| Para probar se creó una conexión con otro nombre (por ejemplo `conexion_test`) y se asignó a los pasos | Los `.ktr` del repo deben usar `conection-mineria-untrm-bd` | Renombrar la conexión local a `conection-mineria-untrm-bd`, `git restore` del `.ktr` y **no subir** el archivo con otro nombre de conexión |

**Comprobar la conexión de los `.ktr` antes de hacer commit:**

```powershell
Select-String -Path pentaho\*.ktr -Pattern "<connection>"
```

Todas las líneas deben decir `<connection>conection-mineria-untrm-bd</connection>`.

---

## 3. Estructura del repositorio

```
dm-trabajo-g2/
├── data/
│   ├── indian_liver_patient.csv                 # Dataset 1 (ILPD)
│   └── Liver_Patient_Dataset__LPD__train.csv    # Dataset 2 (LPD)
├── docs/
│   ├── ETL_GRUPO2.docx                          # Guía de la práctica (referencia principal)
│   ├── Practica_ETL_Pentaho_PostgreSQL_Python_UNTRM.docx
│   ├── Dataset.txt
│   ├── guia_agente_ia.md                        # Este archivo
│   └── referencia/                              # PDFs de contexto (no son entregables)
├── pentaho/
│   ├── t1_ilpd.ktr                              # Completo
│   ├── t2_lpd.ktr                               # Completo
│   ├── t3_integracion.ktr                       # Completo (integración + comunes)
│   └── job_etl.kjb                              # Por crear
├── sql/
│   ├── 01_crear_tablas.sql                      # Tablas del flujo Pentaho
│   └── 02_verificacion.sql                      # Conteos y comparaciones
├── src/dm_trabajo_g2/__init__.py                # Lo creó `uv init`; no se usa, no borrar
├── _descartar/                                  # No se usa (PyCaret, Streamlit, test.csv.xlsx)
├── etl_modelo.py                                # ETL + modelo en Python
└── pyproject.toml, uv.lock, .python-version, README.md
```

### Flujo de Git: cada integrante trabaja en su propia rama

**Nadie hace commit ni push directo a `main`.** Cada parte se trabaja en una rama propia y se integra a `main` con un Pull Request (PR) en GitHub.

| Parte | Rama | Archivo que edita | Depende de |
|---|---|---|---|
| T2 (resto) | `t2-lpd` | `pentaho/t2_lpd.ktr` | `main` actual |
| T3 | `t3-integracion` | `pentaho/t3_integracion.ktr` | T2 ya integrado en `main` |
| Job | `job-etl` | `pentaho/job_etl.kjb` | T2 y T3 ya integrados en `main` |

**Al empezar tu parte:**

```powershell
git checkout main
git pull
git checkout -b t2-lpd          # usa el nombre de tu rama
```

**Mientras trabajas** (commits pequeños, uno por paso o grupo de pasos):

```powershell
git add pentaho/t2_lpd.ktr
git commit -m "T2: renombrar campos e imputar medianas"
git push -u origin t2-lpd       # la primera vez; luego basta con git push
```

**Al terminar:**

1. En GitHub, abre un **Pull Request** de tu rama hacia `main`. En la descripción pon los conteos que obtuviste (por ejemplo `tabla_enfermedades_1 = 18539, E=0`).
2. Otro integrante lo revisa y lo fusiona (**Merge**).
3. Avisa al siguiente integrante.

**Si tu parte depende de otra que se fusionó después de crear tu rama** (por ejemplo, T3 necesita el T2 terminado):

```powershell
git checkout main
git pull
git checkout t3-integracion
git merge main
```

**Reglas:**

- **Cada rama toca solo su archivo** (y, si hace falta, `docs/guia_agente_ia.md` para actualizar la sección 0). No modifiques el `.ktr` de otra parte en tu rama.
- **Los `.ktr` y `.kjb` son XML largo: un conflicto de merge en ellos es muy difícil de resolver.** Si Git reporta un conflicto en un `.ktr`, no lo edites a mano: avisa al grupo antes de seguir.
- No subas archivos generados ni personales: `.venv/`, capturas sueltas, contraseñas.

---

## 4. Los datos

| Característica | Dataset 1: ILPD | Dataset 2: LPD |
|---|---|---|
| Archivo | `indian_liver_patient.csv` | `Liver_Patient_Dataset__LPD__train.csv` |
| Filas | 583 | 30 691 |
| Codificación | UTF-8 | **ISO-8859-1**, fin de línea CRLF |
| Clase | `Dataset` (1 = enfermo, 2 = sano) | `Result` (1 = enfermo, 2 = sano) |
| Celdas vacías | 4 (solo relación A/G) | 5 425: 902 géneros, 2 edades y el resto en columnas numéricas |
| Filas tras quitar sin edad/género | 583 | 29 787 (904 descartadas) |
| Duplicados | 13 | 11 248 |
| Filas finales | **570** | **18 539** |

En el dataset 2 todos los valores no vacíos son numéricos válidos y el género solo tiene `Male`, `Female` o vacío. Las edades son enteras.

**Detalle que rompe flujos:** en el dataset 2, tres encabezados empiezan con un **espacio no separable invisible** (`\xa0`): `" Alkphos Alkaline Phosphotase"`, `" Sgpt Alamine Aminotransferase"` y `" ALB Albumin"`. **Nunca escribas los nombres de campo del dataset 2 a mano**: usa siempre los botones **Get Fields / Get fields to select** y elige de las listas.

### Esquema unificado

| Pos. | Nombre unificado | Dataset 1 | Dataset 2 | Tipo final |
|---|---|---|---|---|
| 1 | edad | Age | Age of the patient | Integer |
| 2 | genero | Gender | Gender of the patient | String(1): M/F |
| 3 | bilirrubina_total | Total_Bilirubin | Total Bilirubin | Number `#.##` |
| 4 | bilirrubina_directa | Direct_Bilirubin | Direct Bilirubin | Number `#.##` |
| 5 | fosfatasa_alcalina | Alkaline_Phosphotase | ␣Alkphos Alkaline Phosphotase | Number `#.#` |
| 6 | alt_sgpt | Alamine_Aminotransferase | ␣Sgpt Alamine Aminotransferase | Number `#.#` |
| 7 | ast_sgot | Aspartate_Aminotransferase | Sgot Aspartate Aminotransferase | Number `#.#` |
| 8 | proteinas_totales | Total_Protiens | Total Protiens | Number `#.##` |
| 9 | albumina | Albumin | ␣ALB Albumin | Number `#.##` |
| 10 | relacion_a_g | Albumin_and_Globulin_Ratio | A/G Ratio Albumin and Globulin Ratio | Number `#.##` |
| 11 | diagnostico | Dataset | Result | Integer: 1 = enfermo, 0 = sano |

(␣ = espacio invisible al inicio.)

---

## 5. Arquitectura y tablas

Flujo: CSV → staging → limpieza en PDI → tablas limpias → integración → comunes → modelo en Python → predicciones.

| Paso | Archivo | Entrada | Salida |
|---|---|---|---|
| T1 | `pentaho/t1_ilpd.ktr` | CSV 1 | `stg_ilpd`, `tabla_enfermedades` |
| T2 | `pentaho/t2_lpd.ktr` | CSV 2 | `stg_lpd`, `tabla_enfermedades_1` |
| T3 | `pentaho/t3_integracion.ktr` | `tabla_enfermedades`, `tabla_enfermedades_1` | `tabla_enfermedades_integrada`, `tabla_comunes` |
| JOB | `pentaho/job_etl.kjb` | T1 → T2 → T3 | Todas |
| PY | `etl_modelo.py` | CSV de `data/` | Tablas `_py` y `tabla_comunes_prediccion` |

### Conteos esperados (úsalos para validar todo)

| Tabla | Filas | Llenada por |
|---|---|---|
| `stg_ilpd` | 583 | T1 |
| `tabla_enfermedades` | 570 | T1 |
| `stg_lpd` | 30 691 | T2 |
| `tabla_enfermedades_1` | 18 539 | T2 |
| `tabla_enfermedades_integrada` | 18 554 (570 + 18 539 − 555) | T3 |
| `tabla_comunes` | 555 | T3 |
| `tabla_enfermedades_py` / `_1_py` / `_integrada_py` | 570 / 18 539 / 18 554 | Python |
| `tabla_comunes_prediccion` | 555 | Python |

**Decisión del grupo:** Python escribe en tablas con sufijo `_py` para no sobrescribir las de Pentaho y poder compararlas (pregunta 3). No cambiar esto sin acordarlo.

---

## 6. Cómo se trabaja en Pentaho (léelo antes de tocar Spoon)

Estas convenciones evitaron todos los errores en T1:

1. **Guarda la transformación antes de configurar rutas.** La variable `${Internal.Entry.Current.Directory}` (carpeta del `.ktr`) solo tiene valor si el archivo ya está guardado en `pentaho/`.
2. **Rutas relativas siempre:** `${Internal.Entry.Current.Directory}/../data/<archivo>.csv`. Nunca `D:/...` ni `C:/...`.
3. **Conectar pasos:** mantener **Shift** y arrastrar desde un paso al otro. Aparece un menú:
   - **Main output of step**: la salida normal. Es la opción por defecto.
   - **Error handling of step**: no la uses.
   - Desde **Filter rows** aparece **Result is TRUE / Result is FALSE**: usa **Result is TRUE** (la flecha muestra un check verde).
4. **Un paso con dos salidas** muestra un aviso "Distribute / Copy". **Elige siempre Copy** (cada fila va a las dos ramas). Distribute reparte las filas y deja ambas ramas incompletas. No marques "don't show this warning anymore".
5. **Nunca hagas clic en los encabezados de columna de las tablas de configuración** (por ejemplo "Type" o "Name"). Eso reordena las filas, y al guardar cambia el orden real de los campos. En CSV file input eso es grave, porque lee las columnas por posición. Si pasa, haz clic en el encabezado `#` para volver al orden 1, 2, 3… o pulsa Get Fields de nuevo.
6. **Las celdas "Format" aceptan texto:** si la lista no trae el formato (por ejemplo `#.##`), escríbelo a mano y pulsa Enter.
7. **Preview de un paso:** selecciona el paso en el lienzo → botón **Preview** de la barra superior (ojo) → **Quick Launch**. El Preview muestra **como máximo 1000 filas**: en T2 no lo uses para contar. Para contar, ejecuta con **Run** y mira **Step Metrics** o el **Logging**.
8. **Ver tipos de un paso:** clic derecho sobre el paso → **Show output fields**.
9. **Leer el log:** `Finished processing (I=, O=, R=, W=, U=, E=)` → R = filas leídas del paso anterior, W = filas escritas al siguiente, O = filas escritas a la base, **E = errores (debe ser 0)**. En CSV file input, `I` incluye el encabezado (583 filas → I=584).
10. **Capturas para el informe (20 % de la nota):** después de cada paso, una captura del Preview; al final, una del Step Metrics o Logging. Ponle a cada paso un **Step name** descriptivo (los de las tablas de abajo) para que las capturas se entiendan.
11. **Avisos que no son errores:** Unique rows muestra "If the incoming data is not sorted..." al pulsar OK. Pulsa **Close**: ya está resuelto con el Sort rows previo.
12. **Guarda con Ctrl+S después de cada paso.**
13. **Duplicar un paso:** selecciónalo en el lienzo, **Ctrl+C** y **Ctrl+V**. La copia conserva la configuración; solo cambia lo necesario (nombre, tabla, valor). Se usó para Leer LPD y Origen LPD en T3.
14. **Preview dentro de un Table input** pide el número de filas: escribe 1000. Los valores de columnas NUMERIC se ven como `460.0` o `152.0`; es normal.

---

## 7. T1 (`t1_ilpd.ktr`): COMPLETO, sirve de referencia

Diagrama final:

```
CSV file input ──(copy)──> Staging stg_ilpd
      │(copy)
      v
Renombrar campos → Limpiar vacios → Filtrar criticos ─(TRUE)→ Imputar mediana → Normalizar genero
→ Mapear genero → Recodificar diagnostico → Convertir tipos → Ordenar filas → Eliminar duplicados
→ Cargar tabla_enfermedades
```

| # | Step name (tipo de paso, categoría) | Act. | Configuración usada |
|---|---|---|---|
| 1 | **CSV file input** (CSV file input, Input) | 1 | Filename `${Internal.Entry.Current.Directory}/../data/indian_liver_patient.csv`; Delimiter `,`; Enclosure `"`; **Lazy conversion desmarcado**; Header row marcado; Encoding **UTF-8**. Get Fields → los 11 campos con Type **String** y Format, Length y Precision vacíos. |
| 2 | **Staging stg_ilpd** (Table output, Output) | 1 | Connection `conection-mineria-untrm-bd`; schema `public`; table `stg_ilpd`; commit 1000; **Truncate table**; Use batch update; **Specify database fields** marcado. Pestaña Database fields → **Enter field mapping** emparejando por posición (Age→age, Gender→gender, Total_Bilirubin→tb, Direct_Bilirubin→db, Alkaline_Phosphotase→alkphos, Alamine_Aminotransferase→sgpt, Aspartate_Aminotransferase→sgot, Total_Protiens→tp, Albumin→alb, Albumin_and_Globulin_Ratio→ag_ratio, Dataset→dataset). **No usar Guess.** |
| 3 | **Renombrar campos** (Select values, Transform) | 2 | Segunda salida del CSV (**Copy**). Pestaña Select & Alter → **Get fields to select** → columna **Rename to** con los 11 nombres unificados en orden. **Include unspecified fields** desmarcado. No hay ID que eliminar. |
| 4 | **Limpiar vacios** (Replace in string, Transform) | 3 | Get fields → 11 filas con use RegEx `Y`, Search `^\s*$`, Replace with vacío, Set empty string `N`, Out stream field vacío. Pentaho trata el texto vacío como nulo. |
| 5 | **Filtrar criticos** (Filter rows, Flow) | 3 | Condición `genero IS NOT NULL` **AND** `edad IS NOT NULL` (la segunda con el botón **+**). Send true/false vacíos; la salida al siguiente paso es **Result is TRUE**. |
| 6 | **Imputar mediana** (If field value is null, Utility) | 3 | **Select fields** marcado, Select value type desmarcado. Fields: `relacion_a_g` = `0.93`. |
| 7 | **Normalizar genero** (String operations, Transform) | 4 | Una sola fila: `genero`, Trim type `both`, Lower/Upper `lower`. No usar Get fields. |
| 8 | **Mapear genero** (Value mapper, Transform) | 4 | Fieldname `genero`; Target field vacío; Default vacío; `male`→`M`, `female`→`F`. |
| 9 | **Recodificar diagnostico** (Value mapper, Transform) | 4 | Fieldname `diagnostico`; `1`→`1`, `2`→`0`. |
| 10 | **Convertir tipos** (Select values, Transform) | 5 | Select & Alter **vacía**. Pestaña Meta-data → **Get fields to change**: `edad` y `diagnostico` Integer formato `#`; `genero` String Length 1; `bilirrubina_total`, `bilirrubina_directa`, `proteinas_totales`, `albumina`, `relacion_a_g` Number formato **`#.##`** (escrito a mano); `fosfatasa_alcalina`, `alt_sgpt`, `ast_sgot` Number formato `#.#`. **Decimal `.`** en todas y Grouping vacío. Length vacío en los Number. |
| 11 | **Ordenar filas** (Sort rows, Transform) | 6 | Get Fields → 11 campos Ascending `Y`. "Only pass unique rows" desmarcado. |
| 12 | **Eliminar duplicados** (Unique rows, Transform) | 6 | **Add counter to output** marcado, Counter field `repeticiones`. Fields to compare: Get → 11 campos, Ignore case `N`. |
| 13 | **Cargar tabla_enfermedades** (Table output, Output) | 8 | Table `tabla_enfermedades`; Truncate; commit 1000; batch update; **Specify database fields** → Get fields → **borrar la fila `repeticiones`** (esa columna no existe en la tabla). |

Resultado verificado: Staging stg_ilpd W=583, Eliminar duplicados R=583 W=570, Cargar tabla_enfermedades O=570, E=0 en todos. `SELECT COUNT(*) FROM tabla_enfermedades;` → 570.

---

## 8. T2 (`t2_lpd.ktr`): dataset 2

T2 se creó con **File → Save as** desde T1, así que ya tiene **todos los pasos de T1**. Solo hay que adaptar algunos.

### 8.1 Ya hecho (Integrante 1)

- **CSV file input:** Filename `${Internal.Entry.Current.Directory}/../data/Liver_Patient_Dataset__LPD__train.csv`, encoding **ISO-8859-1**, Lazy conversion desmarcado, Get Fields con los 11 campos en String y orden 1 a 11 (Age of the patient … Result).
- **Staging stg_lpd:** table `stg_lpd`, mapeo por posición `Age of the patient→age` … `Result→dataset`.

### 8.2 Completado (Integrante 2): paso a paso

Abre `pentaho/t2_lpd.ktr` (después de `git pull`). Revisa primero que la pestaña diga **t2_lpd** y no t1_ilpd.

**Paso 1: Renombrar campos** (actividad 2). Es el paso clave: aquí los nombres largos del dataset 2 pasan al esquema unificado.

1. Doble clic en **Renombrar campos**, pestaña **Select & Alter**.
2. Las filas actuales tienen los nombres del dataset 1 (Age, Gender…). **Borra todas**: selecciónalas (clic en la primera, Shift+clic en la última) y pulsa Supr, o clic derecho → **Delete selected lines**.
3. Pulsa **Get fields to select**. Deben aparecer 11 filas con los nombres del dataset 2, en este orden. **Comprueba el orden y no hagas clic en los encabezados.**
4. En **Rename to** escribe:

| # | Fieldname (no escribirlo, viene de Get fields) | Rename to |
|---|---|---|
| 1 | Age of the patient | edad |
| 2 | Gender of the patient | genero |
| 3 | Total Bilirubin | bilirrubina_total |
| 4 | Direct Bilirubin | bilirrubina_directa |
| 5 | ␣Alkphos Alkaline Phosphotase | fosfatasa_alcalina |
| 6 | ␣Sgpt Alamine Aminotransferase | alt_sgpt |
| 7 | Sgot Aspartate Aminotransferase | ast_sgot |
| 8 | Total Protiens | proteinas_totales |
| 9 | ␣ALB Albumin | albumina |
| 10 | A/G Ratio Albumin and Globulin Ratio | relacion_a_g |
| 11 | Result | diagnostico |

5. **Include unspecified fields** desmarcado. OK y Ctrl+S.
6. Preview de Renombrar campos: primera columna `edad` con edades (65, 62…), `genero` con Male/Female, `diagnostico` con 1/2. Captura.

**Paso 2: Limpiar vacios, Filtrar criticos.** No se cambian: después del renombrado los campos se llaman igual que en T1. Solo revisa:

- Limpiar vacios: las 11 filas siguen con los nombres unificados (`edad` … `diagnostico`), RegEx `Y`, Search `^\s*$`.
- Filtrar criticos: condición `genero IS NOT NULL AND edad IS NOT NULL` y la flecha al siguiente paso con check verde (TRUE).

Aquí sí actúan: en el dataset 2 hay 902 géneros vacíos y 2 edades vacías → **904 filas descartadas**.

**Paso 3: Imputar mediana** (actividad 3). En el dataset 2 hay nulos en las 8 columnas numéricas.

1. Doble clic en **Imputar mediana**. Mantén **Select fields** marcado.
2. En la tabla **Fields**, cambia `relacion_a_g` a `0.90` y agrega 7 filas (escribe el nombre o elígelo de la lista desplegable):

| Field | Replace by value |
|---|---|
| relacion_a_g | 0.90 |
| bilirrubina_total | 1.0 |
| bilirrubina_directa | 0.3 |
| fosfatasa_alcalina | 209 |
| alt_sgpt | 35 |
| ast_sgot | 42 |
| proteinas_totales | 6.6 |
| albumina | 3.1 |

3. Conversion mask y Set empty string vacíos. OK y Ctrl+S.

Son las medianas del dataset 2 (ya sin las filas descartadas). Se escriben como constantes porque este paso no calcula medianas.

**Paso 4: Normalizar genero, Mapear genero, Recodificar diagnostico, Convertir tipos, Ordenar filas, Eliminar duplicados.** No se cambian. Si quieres revisar, deben estar exactamente como en la tabla de T1 (sección 7). En particular, Convertir tipos debe tener **Decimal `.`** en los campos Number.

**Paso 5: Cargar tabla** (actividad 8).

1. Doble clic en **Cargar tabla_enfermedades**.
2. Step name: `Cargar tabla_enfermedades_1`. Target table: `tabla_enfermedades_1`.
3. Pestaña Database fields: deben quedar los 11 campos **sin `repeticiones`**. Si aparece, bórrala.
4. OK y Ctrl+S.

**Paso 6: Ejecutar y validar.** Pulsa **Run** (no Preview). Tarda unos segundos. En **Logging** / **Step Metrics** debe salir:

| Paso | Valor esperado |
|---|---|
| CSV file input | I = 30 692, W = 61 382 (30 691 × 2 por el Copy) |
| Staging stg_lpd | O = 30 691 |
| Renombrar campos, Limpiar vacios | W = 30 691 |
| Filtrar criticos | W = 29 787 |
| Imputar mediana … Ordenar filas | W = 29 787 |
| Eliminar duplicados | R = 29 787, W = 18 539 |
| Cargar tabla_enfermedades_1 | O = 18 539 |
| Todos | E = 0 |

En DBeaver:

```sql
SELECT COUNT(*) FROM stg_lpd;               -- 30691
SELECT COUNT(*) FROM tabla_enfermedades_1;  -- 18539
```

Toma capturas del Step Metrics y de las consultas. Haz commit y push de `t2_lpd.ktr` y avisa al Integrante 3.

**Si algo no coincide:**

- Filtrar criticos con W = 30 691: Limpiar vacios no convierte los vacíos o la condición está mal.
- Valores numéricos ×10 (por ejemplo 9 en vez de 0.9): falta Decimal `.` en Convertir tipos.
- Error "field not found" en Renombrar campos: se escribió un nombre a mano (espacio invisible). Repite Get fields to select.
- Error de columna inexistente al cargar: quedó `repeticiones` en el mapeo.

---

## 9. T3 (`t3_integracion.ktr`): integración (Integrante 3)

**Requisito:** en tu PostgreSQL deben estar llenas `tabla_enfermedades` (570) y `tabla_enfermedades_1` (18 539). Si no, abre y ejecuta T1 y T2 primero.

Diagrama objetivo:

```
Leer ILPD ─(copy)─> Origen ILPD ─┐
     │(copy)                      ├─> Unir datasets → Ordenar para unicos → Eliminar repetidos
     │                            │   → Generar id_paciente → Cargar integrada
Leer LPD ──(copy)─> Origen LPD ──┘
     │(copy)
     v
Ordenar A (desde Leer ILPD) ─┐
                             ├─> Comunes (Merge join INNER) → Quitar campos repetidos → Cargar tabla_comunes
Ordenar B (desde Leer LPD) ──┘
```

### 9.0 Estado actual y cómo continuar (Integrante 3)

**Hecho por el Integrante 1 (pasos 1 a 9, rama de integración), subido a `main` y verificado con Run y en DBeaver (18 554 filas; ILPD 570, LPD 17 984; id_paciente 1 a 18 554):**

```
Leer ILPD (I=570) → Origen ILPD (570) ─┐
                                        ├→ Unir datasets (19 109) → Ordenar para unicos (19 109)
Leer LPD (I=18539) → Origen LPD (18539)┘   → Eliminar repetidos (W=18 554) → Generar id_paciente (18 554)
                                           → Cargar integrada (O=18 554, E=0)
```

**Falta (Integrante 3):** la rama de registros comunes (pasos 10 a 14, sección 9.3), validar todo (9.4) y la demostración de Insert/Update (9.5).

**Cómo traer el trabajo y crear tu rama:** el T3 parcial ya está en `main`, junto con T1 y T2 completos.

```powershell
git checkout main
git pull                             # trae T1, T2 y el T3 parcial
git checkout -b t3-integracion       # tu rama, creada desde main actualizado
Select-String -Path pentaho\*.ktr -Pattern "<connection>"   # todas deben decir conection-mineria-untrm-bd
```

Si ya tenías una rama `t3-integracion` creada antes de este `git pull`, no crees otra: entra en ella y trae lo último con `git checkout t3-integracion` y `git merge main`.

Antes de abrir T3 en Spoon, ejecuta **T1 y T2** en tu PC (Run) para que existan `tabla_enfermedades` (570) y `tabla_enfermedades_1` (18 539). Luego abre `pentaho/t3_integracion.ktr`, ejecuta **Run** y comprueba que el log coincida con el diagrama de arriba antes de agregar pasos.

Al terminar: commit y push en `t3-integracion`, y abre el **Pull Request** de `t3-integracion` hacia `main` con los conteos en la descripción.

### 9.1 Crear la transformación (ya hecho)

**File → New → Transformation** y guarda de inmediato como `pentaho/t3_integracion.ktr`.

### 9.2 Rama de integración (ya hecha; referencia de la configuración)

**Paso 1: Leer ILPD** (Table input, categoría Input).

- Connection `conection-mineria-untrm-bd`.
- SQL (lista explícita de columnas, para fijar el orden):

```sql
SELECT edad, genero, bilirrubina_total, bilirrubina_directa, fosfatasa_alcalina,
       alt_sgpt, ast_sgot, proteinas_totales, albumina, relacion_a_g, diagnostico
FROM tabla_enfermedades
```

- Pulsa **Preview**: 570 filas. Captura.

**Paso 2: Leer LPD** (Table input). Igual, con `FROM tabla_enfermedades_1`. Preview (verás 1000 filas como máximo; es normal).

**Paso 3: Origen ILPD** (Add constants, categoría Transform). Conéctalo desde Leer ILPD (Main output).

- Una fila: Name `origen`, Type `String`, Length `5`, Value `ILPD`.

**Paso 4: Origen LPD** (Add constants). Desde Leer LPD. Name `origen`, Type `String`, Length `5`, Value `LPD`.

**Paso 5: Unir datasets** (Append streams, categoría Flow). Conecta Origen ILPD y Origen LPD hacia este paso.

- **Head hop:** `Origen ILPD`. **Tail hop:** `Origen LPD`.
- Ambas ramas tienen los mismos 12 campos y tipos, por eso Append funciona. Si da error de estructura, revisa que las dos consultas SQL sean idénticas (salvo la tabla) y que ambas constantes sean String de longitud 5.

**Paso 6: Ordenar para unicos** (Sort rows). Desde Unir datasets.

- Get Fields → deben salir 12 campos (los 11 + `origen`), todos Ascending `Y`.
- **Deja `origen` como último campo.** Como "ILPD" va antes que "LPD" alfabéticamente, en los registros repetidos la fila de ILPD queda primero, y la conserva el paso siguiente (igual que en Python).

**Paso 7: Eliminar repetidos** (Unique rows).

- **No marques** Add counter (así no hay que quitar columnas después).
- Fields to compare: **Get** → aparecen 12 → **borra la fila `origen`**. Deben quedar las 11 columnas de datos. Si `origen` se queda, ningún registro común se detecta como repetido.
- Pulsa Close en el aviso de ordenamiento.

**Paso 8: Generar id_paciente** (Add sequence, categoría Transform).

- Name of value: `id_paciente`.
- **Use DB to get sequence** desmarcado; **Use counter to calculate sequence** marcado.
- Start at value `1`, Increment by `1`.

**Paso 9: Cargar integrada** (Table output, Output).

- Table `tabla_enfermedades_integrada`, Truncate, commit 1000, batch update, **Specify database fields**.
- Database fields → Get fields: 13 campos (`edad` … `diagnostico`, `origen`, `id_paciente`). Los nombres coinciden con la tabla.

**Resultado verificado (Integrante 1):** Unir datasets W=19 109; Eliminar repetidos R=19 109, W=18 554; Generar id_paciente 18 554; Cargar integrada O=18 554; E=0 en todos.

Consultas de control en DBeaver (captura para el informe):

```sql
SELECT COUNT(*) FROM tabla_enfermedades_integrada;                -- 18554
SELECT origen, COUNT(*) FROM tabla_enfermedades_integrada
GROUP BY origen ORDER BY origen;                                  -- ILPD 570, LPD 17984
SELECT MIN(id_paciente), MAX(id_paciente) FROM tabla_enfermedades_integrada;  -- 1 y 18554
```

Si ILPD sale con 570, los registros comunes conservaron la fila de ILPD (igual que en Python).

### 9.3 Rama de registros comunes (hecha por el Integrante 3; referencia de la configuración)

Esta rama sale **otra vez** de Leer ILPD y Leer LPD (antes de Add constants, así que **no** lleva `origen`) y busca las filas idénticas en ambos datasets. Hazla **un paso a la vez**, con captura de la ventana antes de pulsar OK.

**Paso 10: Ordenar A** (Sort rows, categoría Transform).

1. Arrastra un **Sort rows** debajo de Leer ILPD.
2. Conéctalo desde **Leer ILPD** con Shift + arrastrar → **Main output of step**.
3. Como Leer ILPD ya tiene una salida (hacia Origen ILPD), aparece el aviso "Distribute / Copy" → **Copy**. Con Distribute, cada rama recibiría solo la mitad de las filas.
4. Doble clic: Step name `Ordenar A`. Pulsa **Get Fields** → deben salir **11 campos** (edad … diagnostico, sin `origen`), todos Ascending `Y`. **No toques los encabezados de columna.** "Only pass unique rows" desmarcado.
5. OK y Ctrl+S.

**Paso 11: Ordenar B** (Sort rows).

1. Copia **Ordenar A** (Ctrl+C, Ctrl+V) y renómbralo `Ordenar B`.
2. Conéctalo desde **Leer LPD** → Main output → aviso → **Copy**.
3. Revisa que tenga los mismos 11 campos, **en el mismo orden** que Ordenar A.
4. OK y Ctrl+S.

**Paso 12: Comunes** (Merge join, categoría Joins).

1. Arrastra un **Merge join** a la derecha de Ordenar A y Ordenar B.
2. Conecta **Ordenar A → Merge join** y **Ordenar B → Merge join** (Main output en ambos).
3. Doble clic y configura:
   - **Step name:** `Comunes`
   - **First step:** `Ordenar A`
   - **Second step:** `Ordenar B`
   - **Join type:** `INNER` (solo las filas que existen en ambos)
   - **Keys for 1st step:** botón **Get key fields** → 11 campos (edad … diagnostico).
   - **Keys for 2nd step:** botón **Get key fields** → 11 campos.
4. Revisa que las **dos listas de claves tengan el mismo orden**, fila por fila. Si una lista trae campos de más o en otro orden, borra y vuelve a usar Get key fields.
5. OK y Ctrl+S. Si aparece un aviso de que las entradas deben estar ordenadas, pulsa Close/OK: ya lo están por Ordenar A y B.

**Paso 13: Quitar campos repetidos** (Select values, categoría Transform).

1. Conéctalo desde **Comunes** (Main output).
2. Merge join entrega **22 campos**: los 11 de A y los 11 de B renombrados con sufijo `_1` (`edad_1`, `genero_1`, … `diagnostico_1`).
3. Doble clic: Step name `Quitar campos repetidos`. Pestaña **Select & Alter** → **Get fields to select** → aparecen 22 filas.
4. **Borra las 11 filas que terminan en `_1`** (selecciónalas con Ctrl+clic y pulsa Supr). Deben quedar las 11 originales, en orden. **Include unspecified fields** desmarcado.
5. OK, Ctrl+S. Preview (Quick Launch): 555 filas, 11 columnas. Captura.

**Paso 14: Cargar tabla_comunes** (Table output, categoría Output).

1. Conéctalo desde **Quitar campos repetidos**.
2. Configura: Step name `Cargar tabla_comunes`; Connection `conection-mineria-untrm-bd`; schema `public`; table `tabla_comunes`; commit 1000; **Truncate table**; **Use batch update**; **Specify database fields**.
3. Pestaña Database fields → **Get fields** → deben ser **11 campos** (sin `_1`, sin `origen`, sin `id_paciente`).
4. OK y Ctrl+S.

### 9.4 Ejecutar y validar T3

Ctrl+S y **Run** (se ejecutan las dos ramas juntas). Esperado en Step Metrics:

| Paso | Valor esperado |
|---|---|
| Leer ILPD / Leer LPD | 570 / 18 539 |
| Leer ILPD / Leer LPD (W, por el Copy) | 1 140 / 37 078 |
| Unir datasets | W = 19 109 |
| Eliminar repetidos | W = 18 554 |
| Cargar integrada | O = 18 554 |
| Ordenar A / Ordenar B | 570 / 18 539 |
| Comunes | W = 555 |
| Quitar campos repetidos | W = 555 |
| Cargar tabla_comunes | O = 555 |
| Todos | E = 0 |

En DBeaver:

```sql
SELECT COUNT(*) FROM tabla_enfermedades_integrada;   -- 18554
SELECT COUNT(*) FROM tabla_comunes;                  -- 555
SELECT origen, COUNT(*) FROM tabla_enfermedades_integrada
GROUP BY origen ORDER BY origen;                     -- ILPD 570, LPD 17984
SELECT MIN(id_paciente), MAX(id_paciente) FROM tabla_enfermedades_integrada;  -- 1, 18554
```

Los 555 comunes salen de los 570 del dataset 1; los otros 15 no están en el dataset 2 o difieren en algún valor.

**Resultado verificado de la versión final (en `main`):** Leer ILPD W=1 140, Leer LPD W=37 078, Unir datasets 19 109, Eliminar repetidos 18 554, Cargar integrada O=18 554, Comunes R=19 109 W=555, Cargar tabla_comunes O=555, E=0 en todos. Desde Leer LPD salen exactamente dos hops (Origen LPD y Ordenar B), ambos con Copy.

**Si algo no coincide:**

- Integrada con 19 109: `origen` quedó en Fields to compare de Unique rows.
- Comunes con 0: las claves del Merge join están en distinto orden, o Ordenar A/B no ordenan por las 11 columnas en el mismo orden.
- Integrada u Origen con la mitad de filas: al conectar Ordenar A u Ordenar B se eligió **Distribute** en vez de **Copy**. Borra el hop y vuelve a conectarlo eligiendo Copy.
- Error al cargar comunes: quedaron campos `_1` en Quitar campos repetidos.

### 9.5 Actividad 8: Insert/Update (demostración) — PENDIENTE

Hazla en un archivo **aparte**, `pentaho/t3_insert_update.ktr`, para no tocar el `t3_integracion.ktr` que usa el job.

La guía pide mostrar la diferencia entre Table output (carga completa) e **Insert/Update** (recarga sin duplicar). Para la captura:

1. Arrastra un **Insert / Update** (categoría Output) **sin conectarlo al flujo principal**, o haz una copia de T3 aparte (`t3_insert_update.ktr`) donde reemplazas Cargar integrada por Insert/Update.
2. Configuración: tabla `tabla_enfermedades_integrada`; **The key(s) to look up the value(s)**: los 10 campos clínicos (`edad`, `genero`, `bilirrubina_total` … `relacion_a_g`), comparator `=`; **Update fields**: `diagnostico` con Update = `Y` y el resto con `N`.
3. Al ejecutarlo sobre la tabla ya cargada no debe insertar filas nuevas (la tabla sigue en 18 554). Captura del paso y del conteo.

No dejes Insert/Update conectado en el `t3_integracion.ktr` que usa el job.

Commit y push de `t3_insert_update.ktr` en su propia rama (por ejemplo `insert-update`) y Pull Request hacia `main`.

---

## 10. Job (`job_etl.kjb`) (Integrante 4): PENDIENTE

### 10.0 Qué es y qué debe lograr

Una **transformación** (`.ktr`) mueve y transforma filas. Un **job** (`.kjb`) no toca filas: **orquesta** transformaciones, es decir, decide qué se ejecuta, en qué orden y qué pasa si algo falla. Este job ejecuta T1 → T2 → T3 en cadena y se detiene si alguna falla.

Diagrama objetivo:

```
Start ──(incondicional)──> T1 ILPD ──(si OK)──> T2 LPD ──(si OK)──> T3 Integracion ──(si OK)──> Success
```

**Requisitos:**

- `t1_ilpd.ktr`, `t2_lpd.ktr` y `t3_integracion.ktr` ya están completos en `main` y funcionan por separado.
- En tu PC: PDI 11, la conexión global `conection-mineria-untrm-bd` (sección 2, paso 4) y las tablas creadas con `sql/01_crear_tablas.sql`. No hace falta llenar tablas antes: el job las llena todas.
- **Antes de empezar, ejecuta T1, T2 y T3 por separado una vez** (Run en cada uno). Si alguno falla solo, también fallará dentro del job; es más fácil corregirlo así.

**Rama de Git:**

```powershell
git checkout main
git pull
git checkout -b job-etl
Select-String -Path pentaho\*.ktr -Pattern "<connection>"   # todas: conection-mineria-untrm-bd
```

### 10.1 Crear el job

1. En Spoon: **File → New → Job** (Ctrl+Alt+N). Se abre una pestaña nueva con el lienzo vacío. Comprueba que el ícono de la pestaña es de **job** (no de transformación).
2. Guarda de inmediato con Ctrl+S como `pentaho\job_etl.kjb`, **en la misma carpeta que los tres `.ktr`**. Esto es obligatorio: las rutas del paso siguiente dependen de esa carpeta.

### 10.2 Agregar las entradas (job entries)

En un job, los elementos del lienzo se llaman **entradas** (job entries), no pasos. En la pestaña **Design**, carpeta **General**, arrastra al lienzo, de izquierda a derecha:

1. **Start** (una sola vez; todo job empieza aquí).
2. **Transformation** tres veces.
3. **Success** (marca el final correcto del job).

### 10.3 Configurar cada Transformation

Doble clic en cada entrada Transformation. Arriba aparecen **Entry name** y el campo de la ruta de la transformación (con botón **Browse**).

| Entry name | Transformation (escribir a mano) |
|---|---|
| `T1 ILPD` | `${Internal.Entry.Current.Directory}/t1_ilpd.ktr` |
| `T2 LPD` | `${Internal.Entry.Current.Directory}/t2_lpd.ktr` |
| `T3 Integracion` | `${Internal.Entry.Current.Directory}/t3_integracion.ktr` |

- **Escribe la ruta a mano.** Si usas Browse, Spoon pone la ruta absoluta (`D:/...`) y el job no funcionará en otras PCs. Si ya la pusiste con Browse, reemplaza todo lo anterior a `t1_ilpd.ktr` por `${Internal.Entry.Current.Directory}/`.
- En un job, `${Internal.Entry.Current.Directory}` es la carpeta del `.kjb`. Como el job y los `.ktr` están en `pentaho/`, **no lleva `../`**.
- Las demás pestañas (Options, Logging, Arguments, Parameters) se dejan como vienen. **Run configuration** queda en `Pentaho local`.
- OK en cada una y Ctrl+S.

Truco: configura `T1 ILPD`, cópiala con Ctrl+C / Ctrl+V dos veces y solo cambia el nombre y el archivo.

### 10.4 Conectar las entradas (hops)

Con **Shift + arrastrar**, en este orden:

1. **Start → T1 ILPD**
2. **T1 ILPD → T2 LPD**
3. **T2 LPD → T3 Integracion**
4. **T3 Integracion → Success**

Los hops de un job tienen **condición**, a diferencia de los de una transformación. Se ve por el ícono y el color de la flecha:

| Aspecto de la flecha | Significado | Dónde va |
|---|---|---|
| Negra con **candado** | Incondicional: siempre continúa | Solo **Start → T1 ILPD** |
| **Verde con check** | Follow when result is true: continúa solo si la entrada anterior terminó bien | Los otros tres |
| Roja con X | Follow when result is false: solo si falló | No usarla en este job |

Revisa cada uno de los tres hops verdes. Si alguno sale negro o rojo: **clic derecho sobre la flecha → Evaluation → Follow when result is true**. Así, si T1 falla, T2 y T3 no se ejecutan y el job termina en error en lugar de cargar datos incompletos.

### 10.5 Revisar Start

Doble clic en **Start**: **Repeat** desmarcado y **Type** = `No Scheduling`. El job se ejecuta una sola vez cuando pulsas Run. OK y Ctrl+S.

### 10.6 Ejecutar y validar

1. Ctrl+S y **Run** (el botón de play). En la ventana de opciones, **Run**.
2. Tarda unos segundos (T2 es el más lento). Cada entrada se marca con un **check verde** al terminar bien.
3. Pestaña **Job metrics** (abajo): las tres transformaciones y Success con resultado **Success**.
4. Pestaña **Logging**: aparecen los logs de las tres transformaciones seguidos. Busca estas líneas y compáralas:

| Línea del log | Esperado |
|---|---|
| `Staging stg_ilpd` / `Cargar tabla_enfermedades` | O = 583 / O = 570 |
| `Staging stg_lpd` / `Cargar tabla_enfermedades_1` | O = 30 691 / O = 18 539 |
| `Cargar integrada` / `Cargar tabla_comunes` | O = 18 554 / O = 555 |
| Todas | E = 0 |
| Final | `Job execution finished` sin `ERROR` |

5. En DBeaver, ejecuta la **consulta A** de `sql/02_verificacion.sql` y comprueba los conteos de la sección 5.

**Capturas para el informe:** el diagrama del job con los cuatro checks verdes, **Job metrics** y el final del **Logging**.

Como todas las cargas tienen **Truncate**, el job vacía y vuelve a llenar las tablas en cada ejecución: puedes ejecutarlo varias veces sin duplicar datos.

### 10.7 Si algo falla

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Unable to load the transformation` / `file not found` | Ruta mal escrita o el `.kjb` no está en `pentaho/` | Revisar la ruta de la entrada (sin `../`, nombre exacto del `.ktr`) y dónde se guardó el job |
| El job se detiene en T1 con error del CSV | `${Internal.Entry.Current.Directory}` apunta a otra carpeta | Comprobar que el `.kjb` está en la misma carpeta que los `.ktr` |
| Error de conexión o `ConnectionMissing` | Falta la conexión global o tiene otro nombre | Sección 2, paso 4, y tabla de problemas |
| `no existe la relación ...` | Faltan las tablas | Ejecutar `sql/01_crear_tablas.sql` en `mineria_untrm` |
| T2 o T3 se ejecutan aunque T1 falló | Hop incondicional en lugar de verde | Evaluation → Follow when result is true |

### 10.8 Terminar

```powershell
git add pentaho/job_etl.kjb docs/guia_agente_ia.md
git commit -m "Job: T1 -> T2 -> T3 con hops condicionales"
git push -u origin job-etl
```

Abre el **Pull Request** de `job-etl` hacia `main` con los conteos del log en la descripción, y actualiza la sección 0 de esta guía.

---

## 11. Verificación final (`sql/02_verificacion.sql`)

Ejecuta en DBeaver, conectado a `mineria_untrm`, después del job:

- **Consulta A:** conteos de todas las tablas. Esperado: 570 / 18 539 / 18 554 / 555 tanto en Pentaho como en Python.
- **Consulta B:** distribución del diagnóstico en la integrada: 71,4 % enfermos y 28,6 % sanos.
- **Consulta C:** acierto de los modelos en los comunes (≈0,71 modelo B, 1,0 modelo A).
- **Consulta D:** compara el dataset 1 de Pentaho con el de Python. **Esperado: 0 filas** (los dos flujos dan lo mismo). Es la evidencia para la pregunta 3.

Captura de cada consulta para el informe.

---

## 12. Flujo en Python (`etl_modelo.py`): HECHO

Cada bloque del script corresponde a un paso de PDI (lo indican los comentarios):

1. Lee los dos CSV (UTF-8 y luego latin1).
2. Limpia: renombra por posición, normaliza género, recodifica la clase (2→0), convierte tipos, descarta filas sin edad/género/diagnóstico, imputa la **mediana de cada dataset** y elimina duplicados.
3. Carga `tabla_enfermedades_py` y `tabla_enfermedades_1_py`.
4. Integra: une, marca los comunes, elimina repetidos (gana ILPD), agrega `id_paciente` y carga `tabla_enfermedades_integrada_py`.
5. **Modelo A:** Random Forest (300 árboles, `class_weight="balanced"`, `random_state=42`) sobre el integrado, prueba del 25 %.
6. **Comprobación de fuga:** entrena con LPD sin comunes y prueba con ILPD.
7. **Modelo B:** solo dataset 1 (570 filas), validación cruzada estratificada de 5 particiones.
8. Carga `tabla_comunes_prediccion` con `prob_modelo_integrado`, `pred_integrado`, `prob_modelo_ilpd`, `pred_ilpd`, `acierto_integrado` y `acierto_ilpd`.

### Resultados de la ejecución del grupo

| Paso | Resultado |
|---|---|
| Dataset 1 | 583 → 583 → 570 (4 celdas imputadas, 13 duplicados) |
| Dataset 2 | 30 691 → 29 787 → 18 539 (5 425 celdas nulas, 904 filas sin datos críticos) |
| Integrada | 18 554 filas, 555 comunes |
| Distribución | 71,4 % enfermos (1), 28,6 % sanos (0) |

| Modelo | Exactitud | Precisión | Recall | F1 | AUC |
|---|---|---|---|---|---|
| A. Integrado (prueba 25 %) | 0,997 | 0,996 | 0,999 | 0,998 | 0,999 |
| B. Solo ILPD (CV 5-fold, n = 570) | 0,711 | — | 0,887 | — | 0,730 |

- Fuga (entrena LPD sin comunes, prueba ILPD): **exactitud 1,0**.
- Acierto en los 555 comunes: **1,0** con A y **0,71** con B.
- Importancia de variables (A): fosfatasa alcalina 0,159, AST 0,156, ALT 0,147, bilirrubina total 0,126, bilirrubina directa 0,112, albúmina 0,104, proteínas 0,102, relación A/G 0,088; edad 0,004 y género 0,000.

Las métricas del modelo B varían un poco entre equipos (AUC entre 0,71 y 0,74), porque son solo 570 registros. **En el informe se citan los números de la ejecución propia, no los de la guía.**

---

## 13. Informe: preguntas y hallazgos clave

Responder las 5 preguntas de la guía y llenar la carátula (estudiantes, docente, ciclo, fecha).

1. **Registros eliminados y por qué es válido.** Dataset 1: 13 duplicados exactos (583 → 570). Dataset 2: 904 filas sin edad o género (no se imputan porque inventarlos distorsiona el análisis) y 11 248 duplicados exactos (29 787 → 18 539). Integración: 555 registros repetidos entre datasets se dejan una sola vez (19 109 → 18 554). Los duplicados exactos no aportan información y sesgan el modelo.
2. **Mediana vs media.** Las enzimas (ALT, AST, fosfatasa alcalina) y las bilirrubinas tienen distribuciones muy sesgadas, con valores extremos (por ejemplo ALT 950 o AST 1500). La mediana es robusta a esos extremos; la media se desplaza hacia ellos.
3. **PDI vs Python.** Las filas finales coinciden (570, 18 539, 18 554, 555) y la consulta D lo confirma. Diferencias posibles a comentar: PDI usa medianas fijas escritas a mano y Python las calcula; PostgreSQL redondea según el tipo NUMERIC y Python usa float64; Python escribe en tablas `_py` con tipos inferidos por pandas.
4. **Modelo A ~99,7 % vs modelo B ~71 %.** El A está inflado: el dataset 2 contiene muchos registros casi idénticos entre sí y versiones de los del dataset 1, lo que provoca fuga de información entre entrenamiento y prueba. La comprobación de fuga (entrenar con LPD y probar con ILPD da 100 %) lo demuestra. Las métricas de A reflejan memorización. En un entorno clínico se usaría el criterio del modelo B (validación honesta, AUC ~0,73); su recall alto (~0,89) es deseable porque reduce los enfermos no detectados.
5. **Enfermedad renal.** El flujo es el mismo. Cambian los nombres de columnas y el esquema unificado, las reglas de limpieza (el dataset CKD de UCI usa `?` como nulo y tiene variables categóricas como `htn`, `dm`, `appet`), las medianas, los mapeos de categorías y de la clase (`ckd`/`notckd` → 1/0).

---

## 14. Reglas para el agente de IA

1. **La referencia es `docs/ETL_GRUPO2.docx`** y este archivo. No inventes requisitos.
2. **Pentaho se configura en la interfaz gráfica.** Da instrucciones de **un paso a la vez**, pide una captura de la ventana de configuración antes de que el usuario pulse OK, y luego el Preview o el log. Compara siempre con los conteos esperados de este archivo.
3. **Revisa en cada captura** que no se hayan reordenado filas (columna `#` en orden), que los tipos y formatos sean los indicados y que el log tenga E=0.
4. **No generes ni edites `.ktr`/`.kjb` como XML** salvo que el usuario lo pida; si lo haces, avisa que no está probado.
5. **No subas credenciales.** La contraseña de PostgreSQL va solo en `PG_URL` o en la conexión local de Spoon.
6. **No cambies nombres de tablas, de pasos de las tablas anteriores ni el nombre de la conexión** (`conection-mineria-untrm-bd`) sin acordarlo con el grupo.
7. **Rutas relativas siempre:** `data/` en Python; `${Internal.Entry.Current.Directory}/../data/` en transformaciones; `${Internal.Entry.Current.Directory}/` en el job.
8. **Recuerda las capturas** al terminar cada paso (20 % de la nota).
9. **Responde en español**, breve y concreto.
10. **No uses `_descartar/`** ni PyCaret salvo que el grupo indique lo contrario.
11. **Al terminar una parte, actualiza la tabla de la sección 0** de este archivo y haz commit.
12. **Git:** trabaja siempre en la rama de tu parte (sección 3). **Nunca hagas commit, push ni merge directo a `main`**: la integración se hace con un Pull Request en GitHub. Antes de crear o cambiar de rama, confirma con el usuario en qué rama está (`git branch --show-current`).
