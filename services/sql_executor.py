"""Ejecución segura de consultas SQL generadas por el asistente.

Ejecuta SQL contra la base de datos relacional local de db.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config import ASSISTANT_MAX_ROWS
from db import ejecutar_consulta
import pandas as pd
from services.sql_generator import SQLValidationResult, validate_sql


@dataclass
class SQLExecutionResult:
  """Resultado de la ejecución de una consulta validada."""

  success: bool
  dataframe: pd.DataFrame
  sql: str
  error: Optional[str] = None
  row_count: int = 0


def execute_readonly_sql(
    sql: str,
    max_rows: Optional[int] = None,
) -> SQLExecutionResult:
  """Valida y ejecuta una consulta de solo lectura contra la base de datos local."""
  limit = max_rows if max_rows is not None else ASSISTANT_MAX_ROWS

  validation: SQLValidationResult = validate_sql(sql)
  if not validation.is_valid:
    return SQLExecutionResult(
        success=False,
        dataframe=pd.DataFrame(),
        sql=sql,
        error=validation.error or "SQL inválido.",
        row_count=0,
    )

  safe_sql = validation.sql

  try:
    df = ejecutar_consulta(safe_sql)
    if df is None:
      df = pd.DataFrame()
  except Exception as exc:  # noqa: BLE001
    return SQLExecutionResult(
        success=False,
        dataframe=pd.DataFrame(),
        sql=safe_sql,
        error=f"Error al ejecutar la consulta: {exc}",
        row_count=0,
    )

  if limit and len(df) > limit:
    df = df.head(limit).copy()

  return SQLExecutionResult(
      success=True,
      dataframe=df,
      sql=safe_sql,
      error=None,
      row_count=len(df),
  )


def dataframe_preview_for_llm(df: pd.DataFrame, max_rows: int = 15) -> str:
  """Serializa un DataFrame a texto compacto para el prompt de explicación."""
  if df is None or df.empty:
    return "(sin filas)"

  preview = df.head(max_rows).copy()
  for col in preview.select_dtypes(include="number").columns:
    preview[col] = preview[col].map(
        lambda x: f"{x:.2f}" if isinstance(x, float) else x
    )
  return preview.to_string(index=False)