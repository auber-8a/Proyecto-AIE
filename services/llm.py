from __future__ import annotations

from config import DEFAULT_LLM_MODEL, GEMINI_API_KEY, LLM_TEMPERATURE
import google.generativeai as genai


class LLMError(Exception):
  """Excepción personalizada para errores del LLM."""

  pass


def is_llm_configured() -> bool:
  """Verifica si la API Key de Gemini está configurada."""
  return bool(GEMINI_API_KEY and GEMINI_API_KEY.strip())


def invoke_gemini(
    prompt: str,
    system_instruction: str = "",
    model: str = DEFAULT_LLM_MODEL,
    temperature: float = LLM_TEMPERATURE,
) -> str:
  """Envía un prompt a la API de Google Gemini y devuelve la respuesta en texto."""
  if not is_llm_configured():
    raise LLMError(
        "Falta configurar GEMINI_API_KEY en .streamlit/secrets.toml"
    )

  try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(
        model_name=model,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
        ),
        system_instruction=system_instruction if system_instruction else None,
    )

    response = gemini_model.generate_content(prompt)
    if response and response.text:
      return response.text.strip()
    return "No se obtuvo respuesta del modelo."
  except Exception as e:
    raise LLMError(f"Error al invocar la API de Gemini: {e}") from e