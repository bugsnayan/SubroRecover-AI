"""
SubroRecover AI - LLM Client & Fallback Engine
Manages Google Gemini API interactions with transparent deterministic local fallback.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("subrorecover.agents.llm")

def get_gemini_client():
    """Returns Gemini client if API key is provided in environment; else None."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        logger.debug(f"Could not initialize google.genai: {e}")
        try:
            import google.generativeai as gai
            gai.configure(api_key=api_key)
            return gai
        except Exception as e2:
            logger.warning(f"Failed to configure Gemini SDK: {e2}")
            return None

def call_llm(prompt: str, system_instruction: str = "", model_name: str = "gemini-1.5-flash") -> Optional[str]:
    """
    Attempts to query Google Gemini. Returns response text if successful, or None to signal fallback.
    """
    client = get_gemini_client()
    if not client:
        return None

    try:
        # Check if google.genai client
        if hasattr(client, "models"):
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={"system_instruction": system_instruction} if system_instruction else None
            )
            return response.text
        # Or google.generativeai
        elif hasattr(client, "GenerativeModel"):
            model = client.GenerativeModel(model_name, system_instruction=system_instruction)
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        logger.warning(f"Live Gemini API invocation encountered error: {e}. Switching to deterministic engine.")
        return None
