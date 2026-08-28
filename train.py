import glob
import os
import unicodedata
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Función de limpieza profunda para eliminar duplicados por tildes y espacios
def limpiar_estandar(texto):
  if not isinstance(texto, str):
    return ""
  # Quitar tildes
  s = (
      unicodedata.normalize("NFKD", texto)
      .encode("ASCII", "ignore")
      .decode("ASCII")
  )
  # Quitar dobles espacios y pasar a mayúsculas
  return " ".join(s.split()).upper().strip()


# 1. Cargar archivos
ruta_datos = os.path.join("data", "Siniestros_Transito_*.csv")
archivos_csv = sorted(glob.glob(ruta_datos))
if not archivos_csv:
  archivos_csv = sorted(glob.glob("Siniestros_Transito_*.csv"))

print(f"Cargando archivos: {archivos_csv}")
dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in archivos_csv]
df = pd.concat(dfs, ignore_index=True)

# 2. Limpiar columnas de texto para eliminar duplicados
columnas_texto = [
    "PROVINCIA",
    "CANTON",
    "MES",
    "DIA",
    "HORA",
    "CLASE",
    "CAUSA",
    "ZONA",
]
for col in columnas_texto:
  df[col] = df[col].apply(limpiar_estandar)


# 3. Target
def etiquetar_severidad(row):
  if row["NUM_FALLECIDO"] > 0:
    return "Fatal"
  elif row["NUM_LESIONADO"] > 0:
    return "Con Lesionados"
  return "Solo Daños Materiales"


df["SEVERIDAD"] = df.apply(etiquetar_severidad, axis=1)

features = ["PROVINCIA", "CANTON", "MES", "DIA", "HORA", "CLASE", "CAUSA", "ZONA"]
X = df[features]
y = df["SEVERIDAD"]

# Mapeo provincia -> cantones sin duplicados
prov_canton_map = (
    df.groupby("PROVINCIA")["CANTON"]
    .unique()
    .apply(lambda arr: sorted(list(arr)))
    .to_dict()
)

catalogos = {
    "PROVINCIAS": sorted(list(prov_canton_map.keys())),
    "PROV_CANTON_MAP": prov_canton_map,
    "MES": [
        "ENERO",
        "FEBRERO",
        "MARZO",
        "ABRIL",
        "MAYO",
        "JUNIO",
        "JULIO",
        "AGOSTO",
        "SEPTIEMBRE",
        "OCTUBRE",
        "NOVIEMBRE",
        "DICIEMBRE",
    ],
    "DIA": [
        "LUNES",
        "MARTES",
        "MIERCOLES",
        "JUEVES",
        "VIERNES",
        "SABADO",
        "DOMINGO",
    ],
    "HORA": sorted(df["HORA"].unique().tolist()),
    "CLASE": sorted(df["CLASE"].unique().tolist()),
    "CAUSA": sorted(df["CAUSA"].unique().tolist()),
    "ZONA": sorted(df["ZONA"].unique().tolist()),
    "ANIOS": sorted(df["ANIO"].unique().tolist()),
}
joblib.dump(catalogos, "catalogos.joblib")

# 4. Pipeline y Entrenamiento
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipeline = Pipeline([
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
    (
        "clf",
        RandomForestClassifier(
            n_estimators=120,
            max_depth=16,
            class_weight="balanced",
            n_jobs=-1,
            random_state=42,
        ),
    ),
])

print("Entrenando modelo...")
pipeline.fit(X_train, y_train)
print(classification_report(y_test, pipeline.predict(X_test)))

joblib.dump(pipeline, "model_accidentes.joblib")
print("Modelo y catálogos exportados.")