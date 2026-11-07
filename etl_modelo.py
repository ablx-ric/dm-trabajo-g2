"""ETL + modelo - Mineria de Datos I - UNTRM (Grupo 2)

Dataset 1: data/indian_liver_patient.csv                 -> tabla_enfermedades_py
Dataset 2: data/Liver_Patient_Dataset__LPD__train.csv    -> tabla_enfermedades_1_py
Integrado                                                -> tabla_enfermedades_integrada_py
Comunes + prediccion                                     -> tabla_comunes_prediccion

Las tablas con sufijo (_py) son las del flujo Python; las de Pentaho conservan el nombre
original (tabla_enfermedades, ...) para poder compararlas (pregunta 3 del informe).

Uso (desde la raiz del proyecto):
    $env:PG_URL = "postgresql+psycopg2://postgres:CLAVE@localhost:5432/mineria_untrm"   # PowerShell
    $env.PG_URL = "postgresql+psycopg2://postgres:CLAVE@localhost:5432/mineria_untrm"   # Nushell
    uv run etl_modelo.py
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sqlalchemy import create_engine

# --------------------------------------------------------------------------- configuracion
DATA = Path(__file__).resolve().parent / "data"
CSV1 = DATA / "indian_liver_patient.csv"
CSV2 = DATA / "Liver_Patient_Dataset__LPD__train.csv"
SUF = os.environ.get("SUFIJO_TABLAS", "_py")        # "" para sobrescribir las tablas de Pentaho

PG_URL = os.environ.get("PG_URL")
if not PG_URL:
    sys.exit("Falta la variable de entorno PG_URL, por ejemplo:\n"
             "  postgresql+psycopg2://postgres:CLAVE@localhost:5432/mineria_untrm")
ENGINE = create_engine(PG_URL)

COLS = ["edad", "genero", "bilirrubina_total", "bilirrubina_directa", "fosfatasa_alcalina",
        "alt_sgpt", "ast_sgot", "proteinas_totales", "albumina", "relacion_a_g", "diagnostico"]
NUM = COLS[:1] + COLS[2:10]
SEED = 42


def rf():
    return RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                  random_state=SEED, n_jobs=-1)


def guardar(df, tabla):
    df.to_sql(tabla, ENGINE, if_exists="replace", index=False, method="multi", chunksize=1000)
    print(f"  -> {tabla}: {len(df)} filas")


# --------------------------------------------------------------------------- E + T
def leer(path):
    for enc in ("utf-8", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            pass
    raise ValueError(f"No se pudo leer {path}")


def limpiar(df, nombre):
    log = {"filas_origen": len(df)}
    df = df.copy()
    df.columns = COLS                                            # Select Values (renombrar por posicion)
    df["genero"] = (df["genero"].astype("string").str.strip().str.lower()   # String Operations
                    .map({"male": "M", "female": "F"}))                      # Value Mapper
    df["diagnostico"] = df["diagnostico"].map({1: 1, 2: 0})      # 1 = hepatopatia, 0 = sano
    for c in NUM:
        df[c] = pd.to_numeric(df[c], errors="coerce")            # Metadata (tipos)
    log["celdas_nulas"] = int(df.isna().sum().sum())
    df = df.dropna(subset=["genero", "edad", "diagnostico"])     # criticos: no se imputan
    log["filas_tras_nulos_criticos"] = len(df)
    for c in NUM[1:]:
        df[c] = df[c].fillna(df[c].median())                     # If field value is null (mediana)
    df["edad"] = df["edad"].astype(int)
    df["diagnostico"] = df["diagnostico"].astype(int)
    df = df.drop_duplicates().reset_index(drop=True)             # Unique Rows
    log["filas_finales"] = len(df)
    print(nombre, log)
    return df


print("== 1. Extraccion y limpieza")
d1 = limpiar(leer(CSV1), "dataset1 (ILPD)")
d2 = limpiar(leer(CSV2), "dataset2 (LPD)")

# --------------------------------------------------------------------------- L (tablas limpias)
print("== 2. Carga de tablas limpias")
guardar(d1, f"tabla_enfermedades{SUF}")
guardar(d2, f"tabla_enfermedades_1{SUF}")

# --------------------------------------------------------------------------- integracion
print("== 3. Integracion")
d1["origen"] = "ILPD"
d2["origen"] = "LPD"
integ = pd.concat([d1, d2], ignore_index=True)                   # Append Streams
en_ambos = (integ.duplicated(subset=COLS, keep=False)
            & integ.groupby(COLS)["origen"].transform("nunique").eq(2))
integ["en_ambos"] = en_ambos
integrada = (integ.sort_values("origen", kind="stable")          # ILPD gana en los comunes
                  .drop_duplicates(subset=COLS, keep="first")    # Unique Rows
                  .reset_index(drop=True))
integrada.insert(0, "id_paciente", np.arange(1, len(integrada) + 1))   # Add sequence
print(f"  integrada {integrada.shape}, comunes {int(integrada.en_ambos.sum())}")
guardar(integrada.drop(columns="en_ambos"), f"tabla_enfermedades_integrada{SUF}")

# --------------------------------------------------------------------------- modelo A (integrado)
print("== 4. Modelo A: dataset integrado (prueba 25 %)")
X = pd.get_dummies(integrada[COLS[:-1]], columns=["genero"], drop_first=True)
y = integrada["diagnostico"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.25, stratify=y, random_state=SEED)
mA = rf().fit(Xtr, ytr)
p, pr = mA.predict(Xte), mA.predict_proba(Xte)[:, 1]
met = {
    "accuracy": accuracy_score(yte, p),
    "precision": precision_score(yte, p),
    "recall": recall_score(yte, p),
    "f1": f1_score(yte, p),
    "auc": roc_auc_score(yte, pr),
}

print({k: round(v, 3) for k, v in met.items()})
print(confusion_matrix(yte, p))
print(pd.Series(mA.feature_importances_, X.columns).sort_values(ascending=False).round(3).to_string())

# Comprobacion de fuga: entrenar con LPD (sin comunes) y probar en ILPD
solo_lpd = integrada[(integrada.origen == "LPD")]
solo_ilpd = integrada[(integrada.origen == "ILPD")]
mf = rf().fit(X.loc[solo_lpd.index], y.loc[solo_lpd.index])
print("  Fuga: entrena LPD (sin comunes) -> prueba ILPD: exactitud",
      round(accuracy_score(y.loc[solo_ilpd.index], mf.predict(X.loc[solo_ilpd.index])), 3))

# --------------------------------------------------------------------------- predicciones fuera de muestra
print("== 5. Predicciones fuera de muestra (5-fold)")
cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
integrada["prob_modelo_integrado"] = np.asarray(
    cross_val_predict(rf(), X, y, cv=cv, method="predict_proba")
)[:, 1].round(4)

# Modelo B: solo dataset 1 (ILPD), referencia realista. Los comunes quedan etiquetados ILPD.
mask = integrada.origen.eq("ILPD")
Xs, ys = X[mask], y[mask]
oof_b = np.asarray(cross_val_predict(rf(), Xs, ys, cv=cv, method="predict_proba"))[:, 1]
print("Modelo B (ILPD) AUC", round(float(roc_auc_score(ys, oof_b)), 3), "acc", round(accuracy_score(ys, oof_b >= .5), 3),
      "recall", round(recall_score(ys, oof_b >= .5), 3), "n", len(ys))
integrada.loc[mask, "prob_modelo_ilpd"] = oof_b.round(4)

com = integrada[integrada.en_ambos].copy()
com["pred_integrado"] = (com.prob_modelo_integrado >= .5).astype(int)
com["pred_ilpd"] = (com.prob_modelo_ilpd >= .5).astype(int)
com["acierto_integrado"] = (com.pred_integrado == com.diagnostico).astype(int)
com["acierto_ilpd"] = (com.pred_ilpd == com.diagnostico).astype(int)
com = com.drop(columns=["en_ambos"])
guardar(com, "tabla_comunes_prediccion")
print("  acierto integrado", round(com.acierto_integrado.mean(), 3),
      "| acierto ilpd", round(com.acierto_ilpd.mean(), 3))
print("Listo.")
