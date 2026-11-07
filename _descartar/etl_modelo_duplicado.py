"""ETL + modelo - Mineria de Datos I - UNTRM
Dataset 1: indian_liver_patient.csv  -> tabla_enfermedades
Dataset 2: Liver_Patient_Dataset__LPD__train.csv -> tabla_enfermedades_1
Integrado -> tabla_enfermedades_integrada ; comunes+prediccion -> tabla_comunes_prediccion
"""

import pandas as pd, numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, cross_val_predict, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    recall_score,
    precision_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
import sys, os

UP = "/mnt/user-data/uploads/"
# Cambiar por: postgresql+psycopg2://postgres:CLAVE@localhost:5432/mineria_untrm
ENGINE = create_engine(
    os.environ.get(
        "PG_URL", "postgresql+psycopg2://postgres:TU_CLAVE@localhost:5432/mineria_untrm"
    )
)
COLS = [
    "edad",
    "genero",
    "bilirrubina_total",
    "bilirrubina_directa",
    "fosfatasa_alcalina",
    "alt_sgpt",
    "ast_sgot",
    "proteinas_totales",
    "albumina",
    "relacion_a_g",
    "diagnostico",
]
NUM = COLS[:1] + COLS[2:10]


def leer(path):
    for enc in ("utf-8", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            pass


def limpiar(df, nombre):
    log = {"filas_origen": len(df)}
    df = df.copy()
    df.columns = COLS  # Select Values (renombrar)
    df["genero"] = (
        df["genero"]
        .astype("string")
        .str.strip()
        .str.lower()  # String Operations
        .map({"male": "M", "female": "F"})
    )  # Value Mapper
    df["diagnostico"] = df["diagnostico"].map({1: 1, 2: 0})  # 1 = hepatopatia, 0 = sano
    for c in NUM:
        df[c] = pd.to_numeric(df[c], errors="coerce")  # Metadata (tipos)
    log["nulos"] = int(df.isna().sum().sum())
    df = df.dropna(subset=["genero", "edad", "diagnostico"])  # criticos sin imputar
    for c in NUM[1:]:
        df[c] = df[c].fillna(df[c].median())  # If field value is null
    df["edad"] = df["edad"].astype(int)
    df["diagnostico"] = df["diagnostico"].astype(int)
    log["filas_tras_nulos"] = len(df)
    df = df.drop_duplicates().reset_index(drop=True)  # Unique Rows
    log["filas_finales"] = len(df)
    print(nombre, log)
    return df, log


d1, _ = limpiar(leer(UP + "indian_liver_patient.csv"), "dataset1")
d2, _ = limpiar(leer(UP + "Liver_Patient_Dataset__LPD__train.csv"), "dataset2")
d1.to_sql("tabla_enfermedades", ENGINE, if_exists="replace", index=False)
d2.to_sql("tabla_enfermedades_1", ENGINE, if_exists="replace", index=False)

# Append Streams + Unique Rows
d1["origen"] = "ILPD"
d2["origen"] = "LPD"
integ = pd.concat([d1, d2], ignore_index=True)
claves = COLS
comunes_mask = integ.duplicated(subset=claves, keep=False) & integ.groupby(claves)[
    "origen"
].transform("nunique").eq(2)
integ["en_ambos"] = comunes_mask
integrada = (
    integ.sort_values("origen")
    .drop_duplicates(subset=claves, keep="first")
    .reset_index(drop=True)
)
integrada["id_paciente"] = np.arange(1, len(integrada) + 1)
print("integrada", integrada.shape, "comunes", int(integrada.en_ambos.sum()))
integrada.to_sql(
    "tabla_enfermedades_integrada", ENGINE, if_exists="replace", index=False
)

# Modelo
X = pd.get_dummies(integrada[COLS[:-1]], columns=["genero"], drop_first=True)
y = integrada["diagnostico"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
rf = RandomForestClassifier(
    n_estimators=300, class_weight="balanced", random_state=42, n_jobs=-1
)
rf.fit(Xtr, ytr)
p = rf.predict(Xte)
pr = rf.predict_proba(Xte)[:, 1]
m = dict(
    accuracy=accuracy_score(yte, p),
    precision=precision_score(yte, p),
    recall=recall_score(yte, p),
    f1=f1_score(yte, p),
    auc=roc_auc_score(yte, pr),
)
print({k: round(v, 3) for k, v in m.items()})
print(confusion_matrix(yte, p))
print(
    pd.Series(rf.feature_importances_, X.columns).sort_values(ascending=False).round(3)
)

# Prediccion fuera de muestra (5-fold)
cv = StratifiedKFold(5, shuffle=True, random_state=42)
mk = lambda: RandomForestClassifier(
    n_estimators=300, class_weight="balanced", random_state=42, n_jobs=-1
)
oof_int = cross_val_predict(mk(), X, y, cv=cv, method="predict_proba")[:, 1]
integrada["prob_modelo_integrado"] = oof_int.round(4)
# Modelo B: solo dataset pequeno (ILPD), referencia realista
mask = integrada.origen.eq("ILPD") | integrada.en_ambos
sub = integrada[mask]
Xs = X[mask]
ys = y[mask]
oof_b = cross_val_predict(mk(), Xs, ys, cv=cv, method="predict_proba")[:, 1]
print(
    "Modelo B (ILPD) AUC",
    round(roc_auc_score(ys, oof_b), 3),
    "acc",
    round(accuracy_score(ys, oof_b >= 0.5), 3),
    "recall",
    round(recall_score(ys, oof_b >= 0.5), 3),
    "n",
    len(ys),
)
integrada.loc[mask, "prob_modelo_ilpd"] = oof_b.round(4)
com = integrada[integrada.en_ambos].copy()
com["pred_integrado"] = (com.prob_modelo_integrado >= 0.5).astype(int)
com["pred_ilpd"] = (com.prob_modelo_ilpd >= 0.5).astype(int)
com = com.drop(columns=["en_ambos"])
com.to_sql("tabla_comunes_prediccion", ENGINE, if_exists="replace", index=False)
print(
    "comunes",
    com.shape,
    "acierto integrado",
    round((com.pred_integrado == com.diagnostico).mean(), 3),
    "acierto ilpd",
    round((com.pred_ilpd == com.diagnostico).mean(), 3),
)
