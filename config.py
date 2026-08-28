from __future__ import annotations

import streamlit as st


def _get_secret(key: str, default: str = "") -> str:
  """Lee de st.secrets de forma segura."""
  try:
    return st.secrets.get(key, default)
  except Exception:
    return default


# ---------------------------------------------------------------------------
# Configuración Google Gemini API
# ---------------------------------------------------------------------------
GEMINI_API_KEY = _get_secret("GEMINI_API_KEY", "")

# Modelos disponibles de Gemini
LLM_MODELS = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 1.5 Flash": "gemini-1.5-flash",
}

DEFAULT_LLM_MODEL = _get_secret("LLM_MODEL", "gemini-2.5-flash")

try:
  LLM_TEMPERATURE = float(_get_secret("LLM_TEMPERATURE", "0.1"))
except Exception:
  LLM_TEMPERATURE = 0.1

try:
  ASSISTANT_MAX_ROWS = int(_get_secret("ASSISTANT_MAX_ROWS", "200"))
except Exception:
  ASSISTANT_MAX_ROWS = 200