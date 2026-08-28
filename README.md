# Sistema de Inferencia y Clasificación de Severidad en Siniestros Viales (Ecuador)

## 1. Definición del Problema
Los siniestros de tránsito representan una de las principales causas de mortalidad y morbilidad en Ecuador. Este proyecto aplica Inteligencia Artificial para predecir la severidad de un accidente (Daños Materiales, Con Lesionados, Fatal) a partir de variables geográficas, temporales y circunstanciales, permitiendo priorizar el despliegue de unidades de emergencia y prevenir puntos críticos de riesgo.

## 2. Núcleo de Inteligencia Artificial
* **Tipo de Resultado:** Predicción probabilística y Toma de Decisiones.
* **Algoritmo:** Random Forest Classifier optimizado con balanceo de clases y pipeline de codificación categórica OneHotEncoder.
* **Métricas:** Evaluado mediante precisión, recall y matriz de confusión sobre 87,616 registros históricos del INEC.

## 3. Arquitectura del Sistema
`Archivos CSV (INEC) -> Pipeline de Transformación -> Scikit-Learn Pipeline (Random Forest) -> Streamlit Web UI`

## 4. Registro de Copiloto IA (Trazabilidad)
* **Modelos Utilizados:** Gemini 2.5 Flash / Claude 3.5 Sonnet / GPT-4o.
* **Prompts Clave:**
  * *"Diseña un pipeline en scikit-learn con OneHotEncoder y RandomForestClassifier para clasificar la severidad de siniestros de tránsito."*
  * *"Crea una interfaz en Streamlit con gráficos Plotly para inferir la probabilidad de fatalidad en tiempo real."*

## 5. Instrucciones de Ejecución
1. Instalar requerimientos: `pip install -r requirements.txt`
2. Entrenar el modelo de IA: `python train.py`
3. Ejecutar la aplicación: `streamlit run app.py`


## Arquitectura del Sistema

```mermaid
flowchart TD
    A[Datos Históricos INEC 2018-2021<br/>87,616 registros] --> B[Pipeline de Limpieza y Estandarización<br/>Pandas / Text Normalizer]
    B --> C[OneHotEncoder<br/>Categorical Features]
    C --> D[RandomForestClassifier<br/>120 Estimadores / Balanced Weights]
    D --> E[Inferencia y Serialización<br/>model_accidentes.joblib]
    E --> F[Aplicación Web Streamlit<br/>Predictor + Dashboard Territorial]


---

#### B. Registro Auditable de Copiloto IA (Requisito estricto de la Rúbrica)
El documento exige evidenciar qué modelos de IA se usaron como copiloto y con qué prompts. Añade esta sección al final de tu `README.md`[cite: 1, 2]:

```markdown
## Registro de Uso de IA como Copiloto (Trazabilidad)

* **Modelos Utilizados:** Gemini 2.5 Flash / Claude 3.5 Sonnet / GPT-4o.
* **Versión:** Agosto 2026.
* **Componentes Asistidos:**
  1. *Estructuración del Pipeline de Scikit-Learn:* Diseño del preprocesamiento con `OneHotEncoder` y balanceo de pesos en `RandomForestClassifier`.
  2. *Optimización Geoespacial en Streamlit:* Configuración de capas `mapbox` sin API Key y estandarización de nombres de cantones[cite: 8].
  3. *Manejo Dinámico de Dependencias:* Vinculación reactiva entre provincias y cantones en los selectores de Streamlit.
* **Prompts Principales Ejecutados:**
  * *"Cómo estructurar un pipeline en scikit-learn que maneje variables categóricas de alta cardinalidad para predecir severidad de accidentes."*
  * *"Genera una función de normalización de texto para unificar inconsistencias en los nombres de cantones y causas del dataset INEC."*
  * *"Configura un mapa de densidad y burbujas en Plotly Express con centrado automático en Ecuador y zoom por rueda habilitado."*