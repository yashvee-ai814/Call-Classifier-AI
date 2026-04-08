# routers/llm.py
#
# This router owns everything related to the LLM (Large Language Model).
# It contains the /classify endpoint, the prompt builder, and the Ollama
# HTTP call. Keeping this in its own file makes it easy to swap out the
# LLM provider later without touching anything else.
#
# Ollama is an open-source tool that lets you run LLMs locally on your machine.
# It exposes a simple HTTP API — we send it a prompt and it returns generated text.

import json
import logging
import os

import httpx
from fastapi import APIRouter, HTTPException

# Import data models from the sibling models.py file
from models import CallReason, CallTranscript

# Logger for this module — log messages will be prefixed with this module's name
logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
# These values can be overridden by setting environment variables, which makes
# the app configurable without changing code (important for Docker / production).

# Base URL of the Ollama server (the LLM runtime)
_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API_URL = f"{_OLLAMA_HOST}/api/generate"

# Which model to use — must already be pulled in Ollama (e.g. `ollama pull <model>`)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")

# ── Router ────────────────────────────────────────────────────────────────────
# APIRouter groups related endpoints together.
# Including this router in main.py with app.include_router() mounts all its
# routes onto the main app — so POST /classify/ becomes available.
router = APIRouter(prefix="/classify", tags=["Classification"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_prompt(transcript: str) -> str:
    """
    Craft the text prompt we send to the LLM.

    A good prompt has three parts:
      1. System role  — tells the model who it is and what it should do
      2. Instructions — explains the exact output format we expect
      3. User input   — the actual transcript to analyse
    """
    return f"""You are an AI assistant specialised in analysing call transcripts for \
Aviva's investment, wealth, and retirement business. Identify the primary reason for \
the call. The calls relate to Aviva products (excluding general insurance): investments, \
retirement planning, wealth management, etc.

Return ONLY a valid JSON object with no extra text, in this exact format:
{{
  "reason": "A concise description of the primary reason for the call",
  "category": "One of: inquiry, advice_request, complaint, account_status, transaction, other"
}}

Transcript: {transcript}

JSON Output:"""


def _parse_llm_response(raw: str) -> dict:
    """
    Parse the LLM's text output into a Python dictionary.

    LLMs sometimes wrap the JSON in extra explanation text, so we first try a
    direct parse and fall back to extracting the JSON block if that fails.
    """
    raw = raw.strip()

    # Happy path — the model returned clean JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Fallback — find the outermost { ... } block and parse just that
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or start >= end:
        raise ValueError(f"No valid JSON object found in LLM response: {raw!r}")

    return json.loads(raw[start : end + 1])


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=CallReason, summary="Classify a call transcript")
def classify_call(transcript: CallTranscript):
    """
    Accepts a call transcript and returns a structured classification.

    - Builds a prompt describing what the LLM should do  
    - Sends it to Ollama running locally  
    - Parses and returns the JSON response as a `CallReason`  
    """
    prompt = _build_prompt(transcript.transcript)

    # Payload format required by Ollama's /api/generate endpoint
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,  # Return the full response at once (not a stream)
    }

    try:
        # httpx.Client is similar to requests — we use it to make the HTTP call.
        # timeout=300 seconds because large LLMs can take a while to respond.
        with httpx.Client(timeout=300.0) as client:
            response = client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()  # Throws if status is 4xx or 5xx
            response_data = response.json()

        # Ollama puts the generated text in the "response" key
        result_text = response_data.get("response") or response_data.get("text")
        if not result_text:
            raise ValueError(f"Unexpected Ollama response format: {response_data}")

        logger.info("LLM raw response: %s", result_text)

        # Convert the LLM's text into a dict, then into our Pydantic model
        result = _parse_llm_response(result_text)
        return CallReason(**result)

    except Exception:
        # Log the full traceback for debugging, but don't leak internals to the caller
        logger.exception("Failed to classify call")
        raise HTTPException(status_code=500, detail="LLM classification failed")
