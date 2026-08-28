import glob
import os
import re
import sqlite3
import unicodedata
import pandas as pd
import streamlit as st


def limpiar_texto(txt):
  if not isinstance(txt, str):
    return ""
  s = (
      unicodedata.normalize("NFKD", str(txt))
      .encode("ASCII", "ignore")
      .decode("ASCII")
  )
  return " ".join(s.split()).upper().strip()


@st.cache_resource
def get_db_connection():
  """Crea el esquema relacional en estrella del Data Warehouse en SQLite usando los CSV."""
  conn = sqlite3.connect(":memory:", check_same_thread=False)

  # Cargar los CSVs
  files = sorted(glob.glob(os.path.join("data", "Siniestros_Transito_*.csv")))
  if not files:
    files = sorted(glob.glob("Siniestros_Transito_*.csv"))

  dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in files]
  df = pd.concat(dfs, ignore_index=True)

  # Normalizar textos
  cols_txt = [
      "PROVINCIA",
      "CANTON",
      "MES",
      "DIA",
      "HORA",
      "CLASE",
      "CAUSA",
      "ZONA",
  ]
  for col in cols_txt:
    if col in df.columns:
      df[col] = df[col].apply(limpiar_texto)

  # 1. Dimensión Tiempo
  dim_tiempo = (
      df[["ANIO", "COD_MES", "MES", "COD_DIA", "DIA", "COD_HORA", "HORA"]]
      .drop_duplicates()
      .reset_index(drop=True)
  )
  dim_tiempo["id_tiempo"] = dim_tiempo.index + 1
  dim_tiempo.columns = [c.lower() for c in dim_tiempo.columns]
  dim_tiempo.to_sql("Dim_Tiempo", conn, index=False, if_exists="replace")

  # 2. Dimensión Ubicación
  dim_ubicacion = (
      df[[
          "COD_PROVINCIA",
          "PROVINCIA",
          "COD_CANTON",
          "CANTON",
          "COD_ZONA",
          "ZONA",
      ]]
      .drop_duplicates()
      .reset_index(drop=True)
  )
  dim_ubicacion["id_ubicacion"] = dim_ubicacion.index + 1
  dim_ubicacion.columns = [c.lower() for c in dim_ubicacion.columns]
  dim_ubicacion.to_sql("Dim_Ubicacion", conn, index=False, if_exists="replace")

  # 3. Dimensión Clase
  dim_clase = (
      df[["COD_CLASE", "CLASE"]].drop_duplicates().reset_index(drop=True)
  )
  dim_clase["id_clase"] = dim_clase.index + 1
  dim_clase.columns = [c.lower() for c in dim_clase.columns]
  dim_clase.to_sql("Dim_Clase", conn, index=False, if_exists="replace")

  # 4. Dimensión Causa
  dim_causa = (
      df[["COD_CAUSA", "CAUSA"]].drop_duplicates().reset_index(drop=True)
  )
  dim_causa["id_causa"] = dim_causa.index + 1
  dim_causa.columns = [c.lower() for c in dim_causa.columns]
  dim_causa.to_sql("Dim_Causa", conn, index=False, if_exists="replace")

  # 5. Tabla de Hechos con Surrogate Keys
  df_fact = df.merge(
      dim_tiempo,
      left_on=[
          "ANIO",
          "COD_MES",
          "MES",
          "COD_DIA",
          "DIA",
          "COD_HORA",
          "HORA",
      ],
      right_on=["anio", "cod_mes", "mes", "cod_dia", "dia", "cod_hora", "hora"],
  )
  df_fact = df_fact.merge(
      dim_ubicacion,
      left_on=[
          "COD_PROVINCIA",
          "PROVINCIA",
          "COD_CANTON",
          "CANTON",
          "COD_ZONA",
          "ZONA",
      ],
      right_on=[
          "cod_provincia",
          "provincia",
          "cod_canton",
          "canton",
          "cod_zona",
          "zona",
      ],
  )
  df_fact = df_fact.merge(
      dim_clase,
      left_on=["COD_CLASE", "CLASE"],
      right_on=["cod_clase", "clase"],
  )
  df_fact = df_fact.merge(
      dim_causa,
      left_on=["COD_CAUSA", "CAUSA"],
      right_on=["cod_causa", "causa"],
  )

  fact_table = df_fact[[
      "id_tiempo",
      "id_ubicacion",
      "id_clase",
      "id_causa",
      "NUM_FALLECIDO",
      "NUM_LESIONADO",
      "TOTAL_VICTIMAS",
  ]].copy()
  fact_table.columns = [
      "id_tiempo",
      "id_ubicacion",
      "id_clase",
      "id_causa",
      "num_fallecido",
      "num_lesionado",
      "total_victimas",
  ]
  fact_table["total_accidentes"] = 1
  fact_table.to_sql("Fact_Accidentes", conn, index=False, if_exists="replace")

  conn.commit()
  return conn


def ejecutar_consulta(sql: str, params: tuple = ()) -> pd.DataFrame:
  """Ejecuta consultas adaptando sintaxis T-SQL a SQLite."""
  conn = get_db_connection()
  try:
    sql_clean = sql

    # Adaptar SELECT TOP N -> LIMIT N
    match = re.search(r"SELECT\s+TOP\s+(\d+)", sql_clean, re.IGNORECASE)
    if match:
      limit_num = match.group(1)
      sql_clean = (
          re.sub(r"SELECT\s+TOP\s+\d+", "SELECT", sql_clean, flags=re.IGNORECASE)
          + f" LIMIT {limit_num}"
      )

    # SQLite usa ? para parámetros posicionales
    sql_clean = sql_clean.replace("%s", "?")
    return pd.read_sql_query(sql_clean, conn, params=params)
  except Exception as e:
    st.error(f"Error en consulta SQL: {e}")
    return pd.DataFrame()