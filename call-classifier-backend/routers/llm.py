# routers/llm.py
# Classification endpoint using Ollama LLM

import json
import logging
import os

import httpx
from fastapi import APIRouter, HTTPException

from models import CallReason, CallTranscript

logger = logging.getLogger(__name__)

# Configuration from environment variables
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

router = APIRouter(prefix="/classify", tags=["Classification"])


def _build_prompt(transcript: str) -> str:
    """Build prompt for LLM."""
    return f"""You are an AI assistant analyzing call transcripts for Aviva's investment and wealth management business. 

Identify the primary reason for the call and return ONLY a JSON object in this format:
{{
  "reason": "Brief description of the reason for the call",
  "category": "One of: inquiry, advice_request, complaint, account_status, transaction, other"
}}

Transcript: {transcript}

JSON Output:"""


@router.post("/", response_model=CallReason)
def classify_call(transcript: CallTranscript):
    """Classify a call transcript using Ollama LLM."""
    prompt = _build_prompt(transcript.transcript)
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        with httpx.Client(timeout=300.0) as client:
            response = client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()

        result_text = response.json()["response"]
        result_dict = json.loads(result_text)
        
        logger.info("Classification result: %s", result_dict.get("category"))
        return CallReason(**result_dict)

    except Exception as e:
        logger.error("Classification failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to classify call")
