"""
Centralized LLM API Client for TDS Question Router
Supports Google Gemma models via Google GenAI SDK and REST API with minimal thinking level.
Configured via .env or environment variables:
    GEMINI_API_KEY: Your API key
    GEMINI_MODEL: Model identifier (default: gemma-4-26b-a4b-it)
"""

import os
import sys
import json
import re
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

try:
    from google import genai
    from google.genai import types as genai_types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

def load_dotenv():
    """Load key-value pairs from .env files into os.environ if not already set."""
    search_dirs = [
        Path(__file__).resolve().parent,
        Path(__file__).resolve().parent.parent,
        Path.cwd()
    ]
    for d in search_dirs:
        env_file = d / ".env"
        if env_file.is_file():
            try:
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("\"'")
                    if k and k not in os.environ:
                        os.environ[k] = v
            except Exception:
                pass

load_dotenv()

DEFAULT_MODEL = "gemma-4-26b-a4b-it"

MODEL_ALIASES = {
    "26b": "gemma-4-26b-a4b-it",
    "gemma-26b": "gemma-4-26b-a4b-it",
    "gemma-26b-it": "gemma-4-26b-a4b-it",
    "gemma-4-26b": "gemma-4-26b-a4b-it",
    "31b": "gemma-4-31b-it",
    "gemma-31b": "gemma-4-31b-it",
    "gemma-4-31b": "gemma-4-31b-it",
    "gemma-31b-it": "gemma-4-31b-it",
}

def get_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "").strip()

def get_model_name() -> str:
    raw = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    return MODEL_ALIASES.get(raw.lower(), raw)

def is_api_configured() -> bool:
    return bool(get_api_key())

def clean_json_text(text: str) -> str:
    """Strip markdown code blocks and extract raw JSON object or array."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if m:
        text = m.group(1).strip()
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]
    return text

async def _call_sdk(prompt: str, model_name: str, api_key: str, temperature: float = 0.1) -> str:
    client = genai.Client(api_key=api_key)
    response = await asyncio.to_thread(
        client.models.generate_content,
        model=model_name,
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=temperature,
            thinking_config=genai_types.ThinkingConfig(thinking_level="minimal")
        )
    )
    if response and response.text:
        return response.text.strip()
    raise RuntimeError(f"SDK returned empty response: {response}")

async def _call_rest(prompt: str, model_name: str, api_key: str, temperature: float = 0.1, timeout: float = 8.0) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    gen_cfg = {
        "temperature": temperature,
        # Gemma/thinking models can spend a large part of the budget on thought
        # parts.  Leave enough room for the actual JSON answer.
        "maxOutputTokens": 8192
    }
    if model_name.startswith("gemini-2.5"):
        # Fast path for the audit batch: Gemini 2.5 supports a thinking budget,
        # and disabling it keeps the request inside the grader's 45 s window.
        gen_cfg["thinkingConfig"] = {"thinkingBudget": 0}
    elif model_name.startswith("gemma"):
        gen_cfg["thinkingConfig"] = {"thinkingLevel": "minimal"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": gen_cfg,
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
        if resp.status_code == 400 and "thinking" in resp.text.lower():
            # Gemini Flash models reject thinkingConfig (or the minimal level);
            # retry with the same request without it.
            payload["generationConfig"].pop("thinkingConfig", None)
            resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
        if resp.status_code != 200:
            raise RuntimeError(f"REST API HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            # Thinking models return a "thought" part followed by the answer.
            # Never return the thought text as the model's answer.
            answer_parts = [p.get("text", "") for p in parts if not p.get("thought")]
            if not answer_parts:
                answer_parts = [p.get("text", "") for p in parts]
            if answer_parts:
                return "".join(answer_parts).strip()
        raise RuntimeError(f"REST API candidate has no parts: {data}")

async def call_llm(
    prompt: str,
    system_instruction: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.1,
    timeout: float = 8.0
) -> str:
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    target_model = model or get_model_name()
    full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

    # 1. Try google-genai SDK with thinking_level="minimal"
    if HAS_GENAI_SDK:
        try:
            return await _call_sdk(full_prompt, target_model, api_key, temperature)
        except Exception as err:
            pass

    # 2. Try REST with thinkingLevel="minimal"
    return await _call_rest(full_prompt, target_model, api_key, temperature, timeout)

async def call_llm_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    model: Optional[str] = None,
    timeout: float = 8.0
) -> Optional[Dict[str, Any]]:
    raw_text = await call_llm(
        prompt=prompt,
        system_instruction=system_instruction,
        model=model,
        temperature=0.1,
        timeout=timeout
    )
    cleaned = clean_json_text(raw_text)
    try:
        return json.loads(cleaned)
    except Exception as exc:
        raise ValueError(f"Failed to parse LLM output as JSON: {exc}. Raw text: {raw_text[:200]}")
