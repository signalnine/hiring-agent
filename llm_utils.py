"""
Utility functions for LLM providers.
"""

import re
import logging
from typing import Any, Dict, Optional
from models import ModelProvider, OllamaProvider, GeminiProvider, AnthropicProvider
from prompt import MODEL_PROVIDER_MAPPING, GEMINI_API_KEY, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON content from markdown code blocks.

    Args:
        response_text: Text that may contain JSON wrapped in markdown code blocks

    Returns:
        Text with markdown code block syntax removed
    """

    response_text = response_text.strip()
    if "<think>" in response_text:
        think_start = response_text.find("<think>")
        think_end = response_text.find("</think>")
        if think_start != -1 and think_end != -1:
            response_text = response_text[:think_start] + response_text[think_end + 8 :]

    # Remove leading ```json if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    # Remove trailing ``` if present
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    # Strip trailing commas before a closing brace/bracket. LLMs occasionally
    # emit `{"a": 1,}` or `[1, 2,]`, which is invalid JSON and crashes
    # json.loads downstream. Safe for our payloads (prose evidence strings don't
    # contain a comma immediately followed by a closing brace/bracket).
    response_text = re.sub(r",(\s*[}\]])", r"\1", response_text)

    return response_text


def initialize_llm_provider(model_name: str) -> Any:
    """
    Initialize the appropriate LLM provider based on the model name.

    Args:
        model_name: The name of the model to use

    Returns:
        An initialized LLM provider (either OllamaProvider or GeminiProvider)
    """
    # Default to Ollama provider
    provider = OllamaProvider()
    model_provider = MODEL_PROVIDER_MAPPING.get(model_name, ModelProvider.OLLAMA)
    if model_provider == ModelProvider.ANTHROPIC:
        if not ANTHROPIC_API_KEY:
            logger.warning("⚠️ Anthropic API key not found. Falling back to Ollama.")
        else:
            logger.info(f"🔄 Using Anthropic API provider with model {model_name}")
            provider = AnthropicProvider(api_key=ANTHROPIC_API_KEY)
    elif model_provider == ModelProvider.GEMINI:
        if not GEMINI_API_KEY:
            logger.warning("⚠️ Gemini API key not found. Falling back to Ollama.")
        else:
            logger.info(f"🔄 Using Google Gemini API provider with model {model_name}")
            provider = GeminiProvider(api_key=GEMINI_API_KEY)
    else:
        logger.info(f"🔄 Using Ollama provider with model {model_name}")
    return provider
