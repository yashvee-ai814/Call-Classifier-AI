# models.py
#
# This file defines the "shape" of the data that flows in and out of the API.
# We use Pydantic models for this — Pydantic automatically validates incoming
# data and raises helpful errors if something is missing or the wrong type.
# FastAPI uses these models to generate documentation and validate requests.

from pydantic import BaseModel


class CallTranscript(BaseModel):
    """
    The data we expect FROM the user when they call the /classify endpoint.
    They must send a JSON body like: { "transcript": "Hello, I want to..." }
    """
    transcript: str  # The raw text of the phone call conversation


class CallReason(BaseModel):
    """
    The data we send BACK to the user after classifying the call.
    The response will look like: { "reason": "...", "category": "..." }
    """
    reason: str    # A short human-readable summary of why the call was made
    category: str  # A label — one of: inquiry, advice_request, complaint,
                   #                   account_status, transaction, other
