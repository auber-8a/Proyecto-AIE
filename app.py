# import glob
# import os
# import unicodedata
# import joblib
# import pandas as pd
# import plotly.express as px
# import streamlit as st

# st.set_page_config(
#     page_title="IA Siniestros Viales Ecuador", page_icon="🚗", layout="wide"
# )

# # Diccionario para ordenamiento cronológico de meses
# MES_ORDEN = {
#     "ENERO": 1,
#     "FEBRERO": 2,
#     "MARZO": 3,
#     "ABRIL": 4,
#     "MAYO": 5,
#     "JUNIO": 6,
#     "JULIO": 7,
#     "AGOSTO": 8,
#     "SEPTIEMBRE": 9,
#     "OCTUBRE": 10,
#     "NOVIEMBRE": 11,
#     "DICIEMBRE": 12,
# }


# def limpiar_estandar(texto):
#   if not isinstance(texto, str):
#     return ""
#   s = (
#       unicodedata.normalize("NFKD", str(texto))
#       .encode("ASCII", "ignore")
#       .decode("ASCII")
#   )
#   return " ".join(s.split()).upper().strip()


# # 1. Carga de modelo y catálogos
# @st.cache_resource
# def load_assets():
#   model = joblib.load("model_accidentes.joblib")
#   catalogos = joblib.load("catalogos.joblib")
#   return model, catalogos


# # 2. Carga de datos históricos
# @st.cache_data
# def load_data():
#   files = sorted(glob.glob(os.path.join("data", "Siniestros_Transito_*.csv")))
#   if not files:
#     files = sorted(glob.glob("Siniestros_Transito_*.csv"))
#   dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in files]
#   df = pd.concat(dfs, ignore_index=True)

#   columnas_texto = [
#       "PROVINCIA",
#       "CANTON",
#       "MES",
#       "DIA",
#       "HORA",
#       "CLASE",
#       "CAUSA",
#       "ZONA",
#   ]
#   for col in columnas_texto:
#     if col in df.columns:
#       df[col] = df[col].apply(limpiar_estandar)

#   df["MES_NUM"] = df["MES"].map(MES_ORDEN)
#   return df


# try:
#   model, cat = load_assets()
#   df_hist = load_data()
# except Exception as e:
#   st.error(f"Error cargando assets: {e}. Ejecuta 'python train.py' primero.")
#   st.stop()

# lista_provincias = cat.get("PROVINCIAS", cat.get("PROVINCIA", []))
# prov_canton_map = cat.get("PROV_CANTON_MAP", {})
# anios_disponibles = sorted(
#     cat.get("ANIOS", df_hist["ANIO"].dropna().unique().tolist())
# )
# meses_disponibles = [
#     "ENERO",
#     "FEBRERO",
#     "MARZO",
#     "ABRIL",
#     "MAYO",
#     "JUNIO",
#     "JULIO",
#     "AGOSTO",
#     "SEPTIEMBRE",
#     "OCTUBRE",
#     "NOVIEMBRE",
#     "DICIEMBRE",
# ]

# st.title("Sistema de Predicción y Análisis de Siniestralidad Vial")
# st.caption(
#     "Modelo de Inteligencia Artificial para la estimación de riesgo y"
#     " análisis espacial en Ecuador."
# )

# tab1, tab2 = st.tabs(
#     ["🔮 Predictor de Severidad (IA)", "📊 Mapa y Análisis Territorial"]
# )

# # =======================================================
# # TAB 1: PREDICTOR
# # =======================================================
# with tab1:
#   st.subheader("Simulador de Escenarios de Riesgo con IA")

#   col1, col2, col3 = st.columns(3)
#   with col1:
#     provincia = st.selectbox("Provincia", lista_provincias, key="pred_prov")
#     cantones_validos = (
#         prov_canton_map.get(provincia, cat.get("CANTON", []))
#         if prov_canton_map
#         else cat.get("CANTON", [])
#     )
#     canton = st.selectbox("Cantón", cantones_validos, key="pred_cant")
#     zona = st.selectbox("Zona", cat["ZONA"])

#   with col2:
#     hora = st.selectbox("Franja Horaria", cat["HORA"])
#     clase = st.selectbox("Tipo / Clase de Accidente", cat["CLASE"])
#     causa = st.selectbox("Causa Probable", cat["CAUSA"])

#   with col3:
#     mes = st.selectbox("Mes", meses_disponibles)
#     dia = st.selectbox("Día de la Semana", cat["DIA"])

#   if st.button("Evaluar Riesgo con IA", type="primary", use_container_width=True):
#     input_df = pd.DataFrame([{
#         "PROVINCIA": provincia,
#         "CANTON": canton,
#         "MES": mes,
#         "DIA": dia,
#         "HORA": hora,
#         "CLASE": clase,
#         "CAUSA": causa,
#         "ZONA": zona,
#     }])

#     prediccion = model.predict(input_df)[0]
#     probabilidades = model.predict_proba(input_df)[0]
#     clases = model.classes_

#     st.markdown("---")
#     res1, res2 = st.columns([1, 2])

#     with res1:
#       st.markdown("#### Diagnóstico del Modelo:")
#       if prediccion == "Fatal":
#         st.error(f"## {prediccion.upper()}")
#         st.markdown("**Alerta:** Alto riesgo de víctimas mortales.")
#       elif prediccion == "Con Lesionados":
#         st.warning(f"## {prediccion.upper()}")
#         st.markdown("**Alerta:** Alta probabilidad de personas heridas.")
#       else:
#         st.success(f"## {prediccion.upper()}")
#         st.markdown("**Aviso:** Predominio de solo daños materiales.")

#     with res2:
#       df_prob = pd.DataFrame(
#           {"Severidad": clases, "Probabilidad": probabilidades}
#       )
#       df_prob["Porcentaje"] = (df_prob["Probabilidad"] * 100).round(1).astype(
#           str
#       ) + "%"

#       fig_bar = px.bar(
#           df_prob,
#           x="Probabilidad",
#           y="Severidad",
#           orientation="h",
#           color="Severidad",
#           text="Porcentaje",
#           title=f"Probabilidad de Severidad ({provincia} - {canton})",
#           color_discrete_map={
#               "Fatal": "#e74c3c",
#               "Con Lesionados": "#f39c12",
#               "Solo Daños Materiales": "#2ecc71",
#           },
#       )
#       fig_bar.update_layout(
#           height=300,
#           showlegend=False,
#           font=dict(size=14),
#           xaxis=dict(tickformat=".0%", range=[0, 1]),
#           margin=dict(l=10, r=40, t=50, b=10),
#       )
#       fig_bar.update_traces(
#           textposition="inside", textfont_size=16, insidetextanchor="middle"
#       )
#       st.plotly_chart(fig_bar, use_container_width=True)

# # =======================================================
# # TAB 2: MAPA TERRITORIAL Y ANALÍTICA AVANZADA
# # =======================================================
# with tab2:
#   st.subheader("Análisis Territorial de Siniestralidad Vial")

#   # Fila 1 de Filtros: Años, Meses y Franja Horaria
#   f1, f2, f3 = st.columns([1.2, 1.8, 1.2])
#   with f1:
#     anios_sel = st.multiselect(
#         "Año(s):",
#         options=anios_disponibles,
#         default=anios_disponibles,
#         key="f_anios",
#     )
#   with f2:
#     meses_sel = st.multiselect(
#         "Mes(es):",
#         options=meses_disponibles,
#         default=meses_disponibles,
#         key="f_meses",
#     )
#   with f3:
#     horas_opciones = ["TODAS"] + sorted(
#         df_hist["HORA"].dropna().unique().tolist()
#     )
#     hora_sel = st.selectbox(
#         "Franja Horaria:", horas_opciones, key="f_hora_sel"
#     )

#   # Fila 2 de Filtros: Causa, Clase y Zona
#   f4, f5, f6 = st.columns([1.5, 1.5, 1])
#   with f4:
#     causas_opciones = ["TODAS"] + sorted(
#         df_hist["CAUSA"].dropna().unique().tolist()
#     )
#     causa_sel = st.selectbox("Causa Probable:", causas_opciones, key="f_causa")
#   with f5:
#     clases_opciones = ["TODAS"] + sorted(
#         df_hist["CLASE"].dropna().unique().tolist()
#     )
#     clase_sel = st.selectbox(
#         "Tipo / Clase de Accidente:", clases_opciones, key="f_clase"
#     )
#   with f6:
#     zonas_opciones = ["TODAS"] + sorted(
#         df_hist["ZONA"].dropna().unique().tolist()
#     )
#     zona_sel = st.selectbox("Zona:", zonas_opciones, key="f_zona")

#   if not anios_sel or not meses_sel:
#     st.warning("Selecciona al menos un año y un mes.")
#     st.stop()

#   # Aplicar filtros cruzados
#   condicion = df_hist["ANIO"].isin(anios_sel) & df_hist["MES"].isin(meses_sel)
#   if hora_sel != "TODAS":
#     condicion = condicion & (df_hist["HORA"] == hora_sel)
#   if causa_sel != "TODAS":
#     condicion = condicion & (df_hist["CAUSA"] == causa_sel)
#   if clase_sel != "TODAS":
#     condicion = condicion & (df_hist["CLASE"] == clase_sel)
#   if zona_sel != "TODAS":
#     condicion = condicion & (df_hist["ZONA"] == zona_sel)

#   df_filtrado = df_hist[condicion]

#   # KPIs
#   m1, m2, m3, m4 = st.columns(4)
#   m1.metric("Total Siniestros", f"{len(df_filtrado):,}")
#   m2.metric("Total Víctimas", f"{int(df_filtrado['TOTAL_VICTIMAS'].sum()):,}")
#   m3.metric("Fallecidos", f"{int(df_filtrado['NUM_FALLECIDO'].sum()):,}")
#   m4.metric("Lesionados", f"{int(df_filtrado['NUM_LESIONADO'].sum()):,}")

#   st.markdown("---")

#   # Coordenadas geográficas de cantones
#   COORDS_CANTONES = {
#       "DISTRITO METROPOLITANO DE QUITO": (-0.1807, -78.4678),
#       "GUAYAQUIL": (-2.1894, -79.8891),
#       "AMBATO": (-1.2491, -78.6168),
#       "SANTO DOMINGO": (-0.2531, -79.1754),
#       "CUENCA": (-2.9001, -79.0059),
#       "MILAGRO": (-2.1340, -79.5942),
#       "PORTOVIEJO": (-1.0546, -80.4545),
#       "LOJA": (-3.9931, -79.2042),
#       "DURAN": (-2.1706, -79.8239),
#       "MANTA": (-0.9677, -80.7089),
#       "IBARRA": (0.3517, -78.1223),
#       "RIOBAMBA": (-1.6636, -78.6546),
#       "LATACUNGA": (-0.9316, -78.6155),
#       "BABAHOYO": (-1.8022, -79.5344),
#       "QUEVEDO": (-1.0286, -79.4635),
#       "MACHALA": (-3.2581, -79.9554),
#       "ESMERALDAS": (0.9682, -79.6517),
#       "TULCAN": (0.8119, -77.7173),
#       "AZOGUES": (-2.7397, -78.8475),
#       "GUARANDA": (-1.5927, -79.0041),
#       "DAULE": (-1.8622, -79.9774),
#       "SAMBORONDON": (-2.0628, -79.7240),
#       "MEJIA": (-0.5103, -78.5681),
#       "RUMINAHUI": (-0.3328, -78.4444),
#       "CAYAMBE": (0.0417, -78.1453),
#       "OTAVALO": (0.2344, -78.2625),
#       "SANTA ELENA": (-2.2262, -80.8587),
#       "SALINAS": (-2.2233, -80.9585),
#       "LA LIBERTAD": (-2.2333, -80.9103),
#       "TENA": (-0.9938, -77.8129),
#       "PUYO": (-1.4837, -77.9986),
#       "NUEVA LOJA": (0.0847, -76.8828),
#       "FRANCISCO DE ORELLANA": (-0.4665, -76.9878),
#       "MACAS": (-2.3087, -78.1114),
#       "ZAMORA": (-4.0692, -78.9566),
#       "SAN CRISTOBAL": (-0.9022, -89.6106),
#       "SANTA CRUZ": (-0.7402, -90.3138),
#       "ALAUSI": (-2.2045, -78.8467),
#       "ATACAMES": (0.8667, -79.8456),
#       "CHONE": (-0.6983, -80.0936),
#       "SANTA ROSA": (-3.4489, -79.9594),
#       "HUAQUILLAS": (-3.4753, -80.2289),
#       "VENTANAS": (-1.4428, -79.4608),
#       "VINCES": (-1.5583, -79.7528),
#       "LA CONCORDIA": (0.0078, -79.3942),
#       "PEDERNALES": (0.0717, -80.0528),
#       "EL CARMEN": (-0.2694, -79.4639),
#       "MONTECRISTI": (-1.0444, -80.6606),
#       "PASAGE": (-3.3267, -79.8067),
#       "PIURA": (-3.6833, -79.6833),
#       "GIRÓN": (-3.1606, -79.1464),
#       "GUALACEO": (-2.8942, -78.7778),
#       "PAUTE": (-2.7772, -78.7583),
#       "SANTA ISABEL": (-3.2758, -79.3142),
#       "SAN MIGUEL": (-1.7083, -79.0433),
#       "SAN LORENZO": (1.2867, -78.8353),
#       "QUININDE": (0.3314, -79.4689),
#       "PEDRO MONCAYO": (0.0167, -78.2167),
#       "PUERTO QUITO": (0.1264, -79.2553),
#       "SAN MIGUEL DE LOS BANCOS": (0.0211, -78.8953),
#       "SALCEDO": (-1.0456, -78.5906),
#       "PUJILI": (-0.9575, -78.6967),
#       "SAQUISILI": (-0.8367, -78.6675),
#       "PELILEO": (-1.3303, -78.5447),
#       "PILLARO": (-1.1739, -78.5392),
#       "BANOS DE AGUA SANTA": (-1.3964, -78.4247),
#       "GUANO": (-1.6067, -78.6306),
#       "COLTA": (-1.7167, -78.7667),
#       "CATAMAYO": (-3.9878, -79.3567),
#       "CALVAS": (-4.3267, -79.5567),
#       "SARAGURO": (-3.6214, -79.2378),
#       "YANTZAZA": (-3.8306, -78.7617),
#       "GUALAQUIZA": (-3.4039, -78.5792),
#       "SUCUA": (-2.4583, -78.1722),
#       "LAGO AGRIO": (0.0847, -76.8828),
#       "SHUSHUFINDI": (-0.1833, -76.6500),
#       "ORELLANA": (-0.4665, -76.9878),
#       "JOYA DE LOS SACHAS": (-0.2983, -76.8583),
#   }

#   df_cantones = (
#       df_filtrado.groupby(["PROVINCIA", "CANTON"])
#       .agg(
#           TOTAL_SINIESTROS=("CLASE", "count"),
#           TOTAL_FALLECIDOS=("NUM_FALLECIDO", "sum"),
#           TOTAL_LESIONADOS=("NUM_LESIONADO", "sum"),
#       )
#       .reset_index()
#   )

#   df_cantones["LAT"] = df_cantones["CANTON"].apply(
#       lambda c: COORDS_CANTONES.get(c, (None, None))[0]
#   )
#   df_cantones["LON"] = df_cantones["CANTON"].apply(
#       lambda c: COORDS_CANTONES.get(c, (None, None))[1]
#   )
#   df_puntos = df_cantones.dropna(subset=["LAT", "LON"]).copy()

#   if len(df_puntos) > 0:
#     # 1. Tamaño ajustado para que hasta 1 siniestro sea visible y se distinga de 10,000
#     import numpy as np

#     # Escala logarítmica/raíz para que el menor valor tenga un tamaño base perceptible
#     df_puntos["TAMANIO_PUNTO"] = 12 + (
#         np.sqrt(df_puntos["TOTAL_SINIESTROS"])
#         / np.sqrt(df_puntos["TOTAL_SINIESTROS"].max())
#         * 35
#     )

#     # 2. Mapa con puntos destacados que se intensifican progresivamente
#     fig_map = px.scatter_mapbox(
#         df_puntos,
#         lat="LAT",
#         lon="LON",
#         size="TAMANIO_PUNTO",
#         color="TOTAL_SINIESTROS",
#         color_continuous_scale=[
#             (0.00, "#fef0d9"),  # Mínimo: Color crema claro muy visible
#             (0.15, "#fdcc8a"),  # Bajo: Naranja claro
#             (0.40, "#fc8d59"),  # Medio: Naranja intenso
#             (0.70, "#e34a33"),  # Alto: Rojo
#             (1.00, "#7f0000"),  # Crítico: Rojo oscuro / Vino
#         ],
#         size_max=45,
#         hover_name="CANTON",
#         hover_data={
#             "PROVINCIA": True,
#             "TOTAL_SINIESTROS": ":,",
#             "TOTAL_FALLECIDOS": ":,",
#             "TOTAL_LESIONADOS": ":,",
#             "TAMANIO_PUNTO": False,
#             "LAT": False,
#             "LON": False,
#         },
#         mapbox_style="open-street-map",
#         center={"lat": -1.4, "lon": -78.4},
#         zoom=6.0,
#         title="Distribución Cantonal de Siniestros Viales (Ecuador)",
#     )

#     fig_map.update_layout(
#         margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=540, dragmode="pan"
#     )
#     st.plotly_chart(
#         fig_map,
#         use_container_width=True,
#         config={"scrollZoom": True, "displayModeBar": True},
#     )
#   else:
#     st.info("No se encontraron registros con los filtros seleccionados.")

#   # =======================================================
#   # ANALÍTICA INFERIOR
#   # =======================================================
#   st.markdown("### Patrones de Comportamiento y Factores de Riesgo")
#   gcol1, gcol2 = st.columns(2)

#   with gcol1:
#     df_top_cantones = df_cantones.sort_values(
#         "TOTAL_SINIESTROS", ascending=True
#     ).tail(10)
#     fig_top_cant = px.bar(
#         df_top_cantones,
#         x="TOTAL_SINIESTROS",
#         y="CANTON",
#         orientation="h",
#         color="TOTAL_SINIESTROS",
#         color_continuous_scale="Reds",
#         text_auto=",.0f",
#         title="Top Cantones con Mayor Número de Siniestros",
#     )
#     fig_top_cant.update_layout(
#         height=380, showlegend=False, margin=dict(l=10, r=20, t=40, b=10)
#     )
#     st.plotly_chart(fig_top_cant, use_container_width=True)

#   with gcol2:
#     orden_dias = [
#         "LUNES",
#         "MARTES",
#         "MIERCOLES",
#         "JUEVES",
#         "VIERNES",
#         "SABADO",
#         "DOMINGO",
#     ]
#     df_heatmap = (
#         df_filtrado.groupby(["DIA", "HORA"])
#         .size()
#         .reset_index(name="CANTIDAD")
#         .pivot(index="DIA", columns="HORA", values="CANTIDAD")
#         .reindex(orden_dias)
#         .fillna(0)
#     )

#     fig_heat_time = px.imshow(
#         df_heatmap,
#         labels=dict(x="Franja Horaria", y="Día", color="Siniestros"),
#         color_continuous_scale="Viridis",
#         title="Mapa de Calor Temporal (Día vs. Horario)",
#         aspect="auto",
#     )
#     fig_heat_time.update_layout(
#         height=380, margin=dict(l=10, r=20, t=40, b=10)
#     )
#     st.plotly_chart(fig_heat_time, use_container_width=True)

#   # Evolución Cronológica
#   st.markdown("#### Evolución Histórica de Siniestros y Víctimas")
#   df_evolucion = (
#       df_filtrado.groupby(["ANIO", "MES_NUM", "MES"])
#       .agg(
#           Siniestros=("CLASE", "count"),
#           Víctimas=("TOTAL_VICTIMAS", "sum"),
#           Fallecidos=("NUM_FALLECIDO", "sum"),
#       )
#       .reset_index()
#       .sort_values(["ANIO", "MES_NUM"])
#   )

#   df_evolucion["PERIODO"] = (
#       df_evolucion["ANIO"].astype(str) + " - " + df_evolucion["MES"]
#   )

#   fig_trend = px.line(
#       df_evolucion,
#       x="PERIODO",
#       y=["Siniestros", "Víctimas", "Fallecidos"],
#       markers=True,
#       title="Tendencia Cronológica de Siniestralidad Vial (2018 - 2021)",
#       color_discrete_map={
#           "Siniestros": "#3498db",
#           "Víctimas": "#f39c12",
#           "Fallecidos": "#e74c3c",
#       },
#   )
#   fig_trend.update_layout(
#       height=380,
#       margin=dict(l=10, r=20, t=40, b=10),
#       hovermode="x unified",
#       xaxis=dict(categoryorder="array", categoryarray=df_evolucion["PERIODO"]),
#   )
#   st.plotly_chart(fig_trend, use_container_width=True)


import glob
import os
import unicodedata
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Estimación de Siniestralidad Vial",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Diccionario de orden cronológico
MES_ORDEN = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SEPTIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12,
}


def limpiar_estandar(texto):
  if not isinstance(texto, str):
    return ""
  s = (
      unicodedata.normalize("NFKD", str(texto))
      .encode("ASCII", "ignore")
      .decode("ASCII")
  )
  return " ".join(s.split()).upper().strip()


# Estilos CSS
st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            max-width: 1200px;
        }
        .header-container {
            padding: 1.2rem 1.5rem;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(56, 189, 248, 0.04) 100%);
            border: 1px solid rgba(56, 189, 248, 0.25);
            margin-bottom: 1.5rem;
        }
        .header-title {
            font-size: 1.6rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin: 0;
        }
        .header-subtitle {
            font-size: 0.92rem;
            opacity: 0.8;
            margin-top: 0.3rem;
            margin-bottom: 0;
        }
        .result-box {
            border-radius: 12px;
            padding: 1.4rem;
            text-align: center;
            border: 1px solid rgba(148, 163, 184, 0.2);
            background-color: var(--secondary-background-color);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .result-tag {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.7;
            margin-bottom: 0.4rem;
        }
        .badge-fatal {
            color: #EF4444;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.01em;
        }
        .badge-lesion {
            color: #F59E0B;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.01em;
        }
        .badge-danos {
            color: #10B981;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.01em;
        }
        .result-desc {
            font-size: 0.85rem;
            opacity: 0.8;
            margin-top: 0.6rem;
            line-height: 1.4;
        }
        .sidebar-metric {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.6rem;
        }
        .sidebar-metric-title {
            font-size: 0.75rem;
            opacity: 0.65;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .sidebar-metric-val {
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: 0.1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_assets():
  model = joblib.load("model_accidentes.joblib")
  catalogos = joblib.load("catalogos.joblib")
  return model, catalogos


@st.cache_data
def load_data():
  files = sorted(glob.glob(os.path.join("data", "Siniestros_Transito_*.csv")))
  if not files:
    files = sorted(glob.glob("Siniestros_Transito_*.csv"))
  dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in files]
  df = pd.concat(dfs, ignore_index=True)

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
    if col in df.columns:
      df[col] = df[col].apply(limpiar_estandar)

  df["MES_NUM"] = df["MES"].map(MES_ORDEN)
  return df


try:
  model, cat = load_assets()
  df_hist = load_data()
except Exception:
  st.error("Archivos requeridos no encontrados. Ejecuta 'python train.py'.")
  st.stop()

# Sidebar informativo
with st.sidebar:
  st.markdown("### Arquitectura del Modelo")
  st.markdown(
      """
        <div class="sidebar-metric">
            <div class="sidebar-metric-title">Algoritmo</div>
            <div class="sidebar-metric-val">Random Forest Classifier</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-title">Registros de Entrenamiento</div>
            <div class="sidebar-metric-val">87,616</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-title">Fuente Oficial</div>
            <div class="sidebar-metric-val">INEC / ANT Ecuador</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-title">Período Histórico</div>
            <div class="sidebar-metric-val">2018 — 2021</div>
        </div>
        """,
      unsafe_allow_html=True,
  )
  st.caption("Entrenamiento estratificado con balanceo ponderado de clases.")

# Encabezado
st.markdown(
    """
    <div class="header-container">
        <h1 class="header-title">Estimación Predictiva y Análisis de Siniestralidad Vial</h1>
        <p class="header-subtitle">Inferencia probabilística de severidad y evaluación espacial de incidentes en Ecuador.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

lista_provincias = cat.get("PROVINCIAS", cat.get("PROVINCIA", []))
prov_canton_map = cat.get("PROV_CANTON_MAP", {})
anios_disponibles = sorted(
    cat.get("ANIOS", df_hist["ANIO"].dropna().unique().tolist())
)
meses_lista = [
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
]
dias_lista = [
    "LUNES",
    "MARTES",
    "MIERCOLES",
    "JUEVES",
    "VIERNES",
    "SABADO",
    "DOMINGO",
]

tab1, tab2 = st.tabs(
    ["Predictor de Severidad (IA)", "Análisis Territorial y Patrones"]
)

# =======================================================
# PESTAÑA 1: PREDICTOR CON IA
# =======================================================
with tab1:
  st.markdown("##### Parámetros del Siniestro")
  col1, col2, col3 = st.columns(3)

  with col1:
    provincia = st.selectbox("Provincia", lista_provincias, key="pred_prov")
    cantones_validos = (
        prov_canton_map.get(provincia, cat.get("CANTON", []))
        if prov_canton_map
        else cat.get("CANTON", [])
    )
    canton = st.selectbox("Cantón", cantones_validos, key="pred_cant")
    zona = st.selectbox(
        "Zona", cat.get("ZONA", ["URBANA", "RURAL"]), key="pred_zona"
    )

  with col2:
    hora = st.selectbox("Franja Horaria", cat.get("HORA", []), key="pred_hora")
    clase = st.selectbox(
        "Tipo de Accidente", cat.get("CLASE", []), key="pred_clase"
    )
    causa = st.selectbox(
        "Causa Probable", cat.get("CAUSA", []), key="pred_causa"
    )

  with col3:
    mes = st.selectbox("Mes", meses_lista, key="pred_mes")
    dia = st.selectbox("Día de la Semana", dias_lista, key="pred_dia")
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    btn_evaluar = st.button(
        "Calcular Probabilidad",
        type="primary",
        use_container_width=True,
        key="btn_predict",
    )

  if btn_evaluar:
    input_df = pd.DataFrame([{
        "PROVINCIA": provincia,
        "CANTON": canton,
        "MES": mes,
        "DIA": dia,
        "HORA": hora,
        "CLASE": clase,
        "CAUSA": causa,
        "ZONA": zona,
    }])

    prediccion = model.predict(input_df)[0]
    probabilidades = model.predict_proba(input_df)[0]
    clases = model.classes_

    st.markdown("---")
    st.markdown("##### Diagnóstico de Riesgo")

    res1, res2 = st.columns([1, 2])

    with res1:
      if prediccion == "Fatal":
        badge_class = "badge-fatal"
        detalle = "Riesgo crítico de pérdidas humanas. Requiere máxima prioridad en el despacho de emergencias."
      elif prediccion == "Con Lesionados":
        badge_class = "badge-lesion"
        detalle = "Alta probabilidad de personas heridas que demandan atención médica prehospitalaria."
      else:
        badge_class = "badge-danos"
        detalle = "Impacto proyectado bajo, limitado a afectaciones materiales."

      st.markdown(
          f"""
                <div class="result-box">
                    <div class="result-tag">Clasificación Predicha</div>
                    <div class="{badge_class}">{prediccion.upper()}</div>
                    <div class="result-desc">{detalle}</div>
                </div>
                """,
          unsafe_allow_html=True,
      )

    with res2:
      df_prob = pd.DataFrame(
          {"Severidad": clases, "Probabilidad": probabilidades}
      )
      df_prob = df_prob.sort_values("Probabilidad", ascending=True)
      df_prob["Label"] = (df_prob["Probabilidad"] * 100).round(1).astype(
          str
      ) + "%"

      fig = px.bar(
          df_prob,
          x="Probabilidad",
          y="Severidad",
          orientation="h",
          color="Severidad",
          text="Label",
          color_discrete_map={
              "Fatal": "#EF4444",
              "Con Lesionados": "#F59E0B",
              "Solo Daños Materiales": "#10B981",
          },
      )
      fig.update_layout(
          height=220,
          showlegend=False,
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          font=dict(size=12),
          xaxis=dict(
              tickformat=".0%",
              range=[0, 1],
              showgrid=True,
              gridcolor="rgba(148, 163, 184, 0.15)",
          ),
          yaxis=dict(showgrid=False, title=None),
          margin=dict(l=10, r=20, t=10, b=10),
      )
      fig.update_traces(
          textposition="inside", textfont_size=13, insidetextanchor="middle"
      )
      st.plotly_chart(fig, use_container_width=True)

# =======================================================
# PESTAÑA 2: ANÁLISIS TERRITORIAL Y PATRONES
# =======================================================
with tab2:
  st.markdown("##### Filtros Multidimensionales")

  f1, f2, f3 = st.columns([1.2, 1.8, 1.2])
  with f1:
    anios_sel = st.multiselect(
        "Año(s):",
        options=anios_disponibles,
        default=anios_disponibles,
        key="map_anios",
    )
  with f2:
    meses_sel = st.multiselect(
        "Mes(es):", options=meses_lista, default=meses_lista, key="map_meses"
    )
  with f3:
    horas_opciones = ["TODAS"] + sorted(
        df_hist["HORA"].dropna().unique().tolist()
    )
    hora_sel = st.selectbox("Franja Horaria:", horas_opciones, key="map_hora")

  f4, f5, f6 = st.columns([1.5, 1.5, 1])
  with f4:
    causas_opciones = ["TODAS"] + sorted(
        df_hist["CAUSA"].dropna().unique().tolist()
    )
    causa_sel = st.selectbox("Causa Probable:", causas_opciones, key="map_causa")
  with f5:
    clases_opciones = ["TODAS"] + sorted(
        df_hist["CLASE"].dropna().unique().tolist()
    )
    clase_sel = st.selectbox(
        "Tipo de Accidente:", clases_opciones, key="map_clase"
    )
  with f6:
    zonas_opciones = ["TODAS"] + sorted(
        df_hist["ZONA"].dropna().unique().tolist()
    )
    zona_sel = st.selectbox("Zona:", zonas_opciones, key="map_zona")

  if not anios_sel or not meses_sel:
    st.warning("Selecciona al menos un año y un mes.")
    st.stop()

  # Aplicar filtros
  condicion = df_hist["ANIO"].isin(anios_sel) & df_hist["MES"].isin(meses_sel)
  if hora_sel != "TODAS":
    condicion = condicion & (df_hist["HORA"] == hora_sel)
  if causa_sel != "TODAS":
    condicion = condicion & (df_hist["CAUSA"] == causa_sel)
  if clase_sel != "TODAS":
    condicion = condicion & (df_hist["CLASE"] == clase_sel)
  if zona_sel != "TODAS":
    condicion = condicion & (df_hist["ZONA"] == zona_sel)

  df_filtrado = df_hist[condicion]

  # KPIs
  st.markdown("<br>", unsafe_allow_html=True)
  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Total Siniestros", f"{len(df_filtrado):,}")
  m2.metric("Total Víctimas", f"{int(df_filtrado['TOTAL_VICTIMAS'].sum()):,}")
  m3.metric("Fallecidos", f"{int(df_filtrado['NUM_FALLECIDO'].sum()):,}")
  m4.metric("Lesionados", f"{int(df_filtrado['NUM_LESIONADO'].sum()):,}")

  st.markdown("---")

  # Coordenadas geográficas de cantones
  COORDS_CANTONES = {
      "DISTRITO METROPOLITANO DE QUITO": (-0.1807, -78.4678),
      "GUAYAQUIL": (-2.1894, -79.8891),
      "AMBATO": (-1.2491, -78.6168),
      "SANTO DOMINGO": (-0.2531, -79.1754),
      "CUENCA": (-2.9001, -79.0059),
      "MILAGRO": (-2.1340, -79.5942),
      "PORTOVIEJO": (-1.0546, -80.4545),
      "LOJA": (-3.9931, -79.2042),
      "DURAN": (-2.1706, -79.8239),
      "MANTA": (-0.9677, -80.7089),
      "IBARRA": (0.3517, -78.1223),
      "RIOBAMBA": (-1.6636, -78.6546),
      "LATACUNGA": (-0.9316, -78.6155),
      "BABAHOYO": (-1.8022, -79.5344),
      "QUEVEDO": (-1.0286, -79.4635),
      "MACHALA": (-3.2581, -79.9554),
      "ESMERALDAS": (0.9682, -79.6517),
      "TULCAN": (0.8119, -77.7173),
      "AZOGUES": (-2.7397, -78.8475),
      "GUARANDA": (-1.5927, -79.0041),
      "DAULE": (-1.8622, -79.9774),
      "SAMBORONDON": (-2.0628, -79.7240),
      "MEJIA": (-0.5103, -78.5681),
      "RUMINAHUI": (-0.3328, -78.4444),
      "CAYAMBE": (0.0417, -78.1453),
      "OTAVALO": (0.2344, -78.2625),
      "SANTA ELENA": (-2.2262, -80.8587),
      "SALINAS": (-2.2233, -80.9585),
      "LA LIBERTAD": (-2.2333, -80.9103),
      "TENA": (-0.9938, -77.8129),
      "PUYO": (-1.4837, -77.9986),
      "NUEVA LOJA": (0.0847, -76.8828),
      "FRANCISCO DE ORELLANA": (-0.4665, -76.9878),
      "MACAS": (-2.3087, -78.1114),
      "ZAMORA": (-4.0692, -78.9566),
      "SAN CRISTOBAL": (-0.9022, -89.6106),
      "SANTA CRUZ": (-0.7402, -90.3138),
      "ALAUSI": (-2.2045, -78.8467),
      "ATACAMES": (0.8667, -79.8456),
      "CHONE": (-0.6983, -80.0936),
      "SANTA ROSA": (-3.4489, -79.9594),
      "HUAQUILLAS": (-3.4753, -80.2289),
      "VENTANAS": (-1.4428, -79.4608),
      "VINCES": (-1.5583, -79.7528),
      "LA CONCORDIA": (0.0078, -79.3942),
      "PEDERNALES": (0.0717, -80.0528),
      "EL CARMEN": (-0.2694, -79.4639),
      "MONTECRISTI": (-1.0444, -80.6606),
      "PASAGE": (-3.3267, -79.8067),
      "PIURA": (-3.6833, -79.6833),
      "GIRÓN": (-3.1606, -79.1464),
      "GUALACEO": (-2.8942, -78.7778),
      "PAUTE": (-2.7772, -78.7583),
      "SANTA ISABEL": (-3.2758, -79.3142),
      "SAN MIGUEL": (-1.7083, -79.0433),
      "SAN LORENZO": (1.2867, -78.8353),
      "QUININDE": (0.3314, -79.4689),
      "PEDRO MONCAYO": (0.0167, -78.2167),
      "PUERTO QUITO": (0.1264, -79.2553),
      "SAN MIGUEL DE LOS BANCOS": (0.0211, -78.8953),
      "SALCEDO": (-1.0456, -78.5906),
      "PUJILI": (-0.9575, -78.6967),
      "SAQUISILI": (-0.8367, -78.6675),
      "PELILEO": (-1.3303, -78.5447),
      "PILLARO": (-1.1739, -78.5392),
      "BANOS DE AGUA SANTA": (-1.3964, -78.4247),
      "GUANO": (-1.6067, -78.6306),
      "COLTA": (-1.7167, -78.7667),
      "CATAMAYO": (-3.9878, -79.3567),
      "CALVAS": (-4.3267, -79.5567),
      "SARAGURO": (-3.6214, -79.2378),
      "YANTZAZA": (-3.8306, -78.7617),
      "GUALAQUIZA": (-3.4039, -78.5792),
      "SUCUA": (-2.4583, -78.1722),
      "LAGO AGRIO": (0.0847, -76.8828),
      "SHUSHUFINDI": (-0.1833, -76.6500),
      "ORELLANA": (-0.4665, -76.9878),
      "JOYA DE LOS SACHAS": (-0.2983, -76.8583),
  }

  df_cantones = (
      df_filtrado.groupby(["PROVINCIA", "CANTON"])
      .agg(
          TOTAL_SINIESTROS=("CLASE", "count"),
          TOTAL_FALLECIDOS=("NUM_FALLECIDO", "sum"),
          TOTAL_LESIONADOS=("NUM_LESIONADO", "sum"),
      )
      .reset_index()
  )

  df_cantones["LAT"] = df_cantones["CANTON"].apply(
      lambda c: COORDS_CANTONES.get(c, (None, None))[0]
  )
  df_cantones["LON"] = df_cantones["CANTON"].apply(
      lambda c: COORDS_CANTONES.get(c, (None, None))[1]
  )
  df_puntos = df_cantones.dropna(subset=["LAT", "LON"]).copy()

  if len(df_puntos) > 0:
    df_puntos["TAMANIO_PUNTO"] = 12 + (
        np.sqrt(df_puntos["TOTAL_SINIESTROS"])
        / np.sqrt(df_puntos["TOTAL_SINIESTROS"].max())
        * 35
    )

    fig_map = px.scatter_mapbox(
        df_puntos,
        lat="LAT",
        lon="LON",
        size="TAMANIO_PUNTO",
        color="TOTAL_SINIESTROS",
        color_continuous_scale=[
            (0.00, "#fef0d9"),
            (0.15, "#fdcc8a"),
            (0.40, "#fc8d59"),
            (0.70, "#e34a33"),
            (1.00, "#7f0000"),
        ],
        size_max=45,
        hover_name="CANTON",
        hover_data={
            "PROVINCIA": True,
            "TOTAL_SINIESTROS": ":,",
            "TOTAL_FALLECIDOS": ":,",
            "TOTAL_LESIONADOS": ":,",
            "TAMANIO_PUNTO": False,
            "LAT": False,
            "LON": False,
        },
        mapbox_style="open-street-map",
        center={"lat": -1.4, "lon": -78.4},
        zoom=6.0,
        title="Concentración Cantonal de Siniestros Viales",
    )

    fig_map.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=540, dragmode="pan"
    )
    st.plotly_chart(
        fig_map,
        use_container_width=True,
        config={"scrollZoom": True, "displayModeBar": True},
    )
  else:
    st.info("No se encontraron registros con los filtros seleccionados.")

  # Gráficos de Analítica
  st.markdown("---")
  st.markdown("##### Patrones de Comportamiento y Factores de Riesgo")
  gcol1, gcol2 = st.columns(2)

  with gcol1:
    df_top_cantones = df_cantones.sort_values(
        "TOTAL_SINIESTROS", ascending=True
    ).tail(10)
    fig_top_cant = px.bar(
        df_top_cantones,
        x="TOTAL_SINIESTROS",
        y="CANTON",
        orientation="h",
        color="TOTAL_SINIESTROS",
        color_continuous_scale="Reds",
        text_auto=",.0f",
        title="Top 10 Cantones con Mayor Número de Siniestros",
    )
    fig_top_cant.update_layout(
        height=380, showlegend=False, margin=dict(l=10, r=20, t=40, b=10)
    )
    st.plotly_chart(fig_top_cant, use_container_width=True)

  with gcol2:
    orden_dias = [
        "LUNES",
        "MARTES",
        "MIERCOLES",
        "JUEVES",
        "VIERNES",
        "SABADO",
        "DOMINGO",
    ]
    df_heatmap = (
        df_filtrado.groupby(["DIA", "HORA"])
        .size()
        .reset_index(name="CANTIDAD")
        .pivot(index="DIA", columns="HORA", values="CANTIDAD")
        .reindex(orden_dias)
        .fillna(0)
    )

    fig_heat_time = px.imshow(
        df_heatmap,
        labels=dict(x="Franja Horaria", y="Día", color="Siniestros"),
        color_continuous_scale="Viridis",
        title="Matriz de Calor Temporal (Día vs. Horario)",
        aspect="auto",
    )
    fig_heat_time.update_layout(
        height=380, margin=dict(l=10, r=20, t=40, b=10)
    )
    st.plotly_chart(fig_heat_time, use_container_width=True)

  # Evolución Cronológica
  st.markdown("##### Evolución Cronológica de Siniestros y Víctimas")
  df_evolucion = (
      df_filtrado.groupby(["ANIO", "MES_NUM", "MES"])
      .agg(
          Siniestros=("CLASE", "count"),
          Víctimas=("TOTAL_VICTIMAS", "sum"),
          Fallecidos=("NUM_FALLECIDO", "sum"),
      )
      .reset_index()
      .sort_values(["ANIO", "MES_NUM"])
  )

  df_evolucion["PERIODO"] = (
      df_evolucion["ANIO"].astype(str) + " - " + df_evolucion["MES"]
  )

  fig_trend = px.line(
      df_evolucion,
      x="PERIODO",
      y=["Siniestros", "Víctimas", "Fallecidos"],
      markers=True,
      title="Tendencia Cronológica de Siniestralidad Vial (2018 - 2021)",
      color_discrete_map={
          "Siniestros": "#3498db",
          "Víctimas": "#f39c12",
          "Fallecidos": "#e74c3c",
      },
  )
  fig_trend.update_layout(
      height=380,
      margin=dict(l=10, r=20, t=40, b=10),
      hovermode="x unified",
      xaxis=dict(categoryorder="array", categoryarray=df_evolucion["PERIODO"]),
  )
  st.plotly_chart(fig_trend, use_container_width=True)