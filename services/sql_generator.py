from __future__ import annotations

from dataclasses import dataclass
import re
from config import DEFAULT_LLM_MODEL
from services.llm import invoke_gemini

ESQUEMA_BD = """
Tablas disponibles en SQLite:
1. Fact_Accidentes (id_tiempo, id_ubicacion, id_clase, id_causa, num_fallecido, num_lesionado, total_victimas, total_accidentes)
2. Dim_Tiempo (id_tiempo, anio, cod_mes, mes, cod_dia, dia, cod_hora, hora)
3. Dim_Ubicacion (id_ubicacion, cod_provincia, provincia, cod_canton, canton, cod_zona, zona)
4. Dim_Clase (id_clase, cod_clase, clase)
5. Dim_Causa (id_causa, cod_causa, causa)
"""


@dataclass
class SQLGenerationResult:

  sql: str
  chart_hint: str
  reasoning: str


@dataclass
class SQLValidationResult:

  is_valid: bool
  sql: str
  error: str | None = None


def generate_sql(
    question: str, model: str = DEFAULT_LLM_MODEL
) -> SQLGenerationResult:
  system_prompt = f"""
    Eres un asistente experto en bases de datos SQLite y analítica vial en Ecuador.
    {ESQUEMA_BD}
    
    Genera ÚNICAMENTE una consulta SQL válida (SELECT de solo lectura) para responder a la pregunta.
    No incluyas explicaciones ni bloques de código markdown dentro del tag de SQL.
    Responde con este formato exacto:
    SQL: <consulta SQL en una sola línea o multilínea>
    CHART: <bar|line|pie|table>
    REASONING: <breve justificación de las tablas y joins usados>
    """

  raw_response = invoke_gemini(
      prompt=f"Pregunta del usuario: {question}",
      system_instruction=system_prompt,
      model=model,
  )

  sql_match = re.search(r"SQL:\s*(.*?)(?=\nCHART:|\nREASONING:|$)", raw_response, re.DOTALL | re.IGNORECASE)
  chart_match = re.search(r"CHART:\s*(\w+)", raw_response, re.IGNORECASE)
  reasoning_match = re.search(r"REASONING:\s*(.*)", raw_response, re.DOTALL | re.IGNORECASE)

  sql = (
      sql_match.group(1).replace("```sql", "").replace("```", "").strip()
      if sql_match
      else raw_response.strip()
  )
  chart = chart_match.group(1).lower().strip() if chart_match else "bar"
  reasoning = (
      reasoning_match.group(1).strip()
      if reasoning_match
      else "Consulta construida a partir del esquema dimensional."
  )

  return SQLGenerationResult(sql=sql, chart_hint=chart, reasoning=reasoning)


def validate_sql(sql: str) -> SQLValidationResult:
  sql_clean = sql.strip().strip(";")
  forbidden = [
      "INSERT",
      "UPDATE",
      "DELETE",
      "DROP",
      "ALTER",
      "CREATE",
      "TRUNCATE",
  ]
  for keyword in forbidden:
    if re.search(rf"\b{keyword}\b", sql_clean, re.IGNORECASE):
      return SQLValidationResult(
          is_valid=False,
          sql="",
          error=f"Operación no permitida: {keyword}",
      )

  if not sql_clean.upper().startswith("SELECT"):
    return SQLValidationResult(
        is_valid=False,
        sql="",
        error="La consulta debe ser un SELECT.",
    )

  return SQLValidationResult(is_valid=True, sql=sql_clean, error=None)


def generate_explanation(
    question: str, sql: str, result_preview: str, model: str = DEFAULT_LLM_MODEL
) -> str:
  prompt = f"""
    Pregunta original: {question}
    SQL Ejecutado: {sql}
    Resultados obtenidos:
    {result_preview}
    
    Explica de forma clara, concisa y profesional en español los hallazgos principales encontrados en estos datos.
    """
  return invoke_gemini(prompt=prompt, model=model)