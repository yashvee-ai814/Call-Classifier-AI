# main.py
#
# This is the entry point for the FastAPI application.
# Its responsibilities are intentionally kept small:
#   1. Create the FastAPI app instance
#   2. Apply middleware (CORS, etc.)
#   3. Register routers (groups of endpoints)
#
# Business logic (LLM calls, data models) lives in their own modules —
# this keeps main.py clean and easy to navigate.

import logging

from fastapi import FastAPI

from middleware import add_middleware
from routers import llm

# Set up logging so all INFO-level messages appear in the terminal.
# You'll see request logs, LLM responses, and any errors here.
logging.basicConfig(level=logging.INFO)

# ── App instance ──────────────────────────────────────────────────────────────
# FastAPI() creates the web application. The metadata here powers the automatic
# interactive API docs available at http://localhost:8000/docs
app = FastAPI(
    title="Call Classifier",
    description="Classifies call transcripts using a local LLM via Ollama.",
    version="1.0.0",
)

# ── Middleware ─────────────────────────────────────────────────────────────────
# Middleware wraps every request. We register it here but define it in middleware.py
add_middleware(app)

# ── Routers ────────────────────────────────────────────────────────────────────
# Routers are groups of related endpoints. Including a router here mounts all
# its routes onto the app — e.g. POST /classify/ defined in routers/llm.py
app.include_router(llm.router)

# ── Dev server ─────────────────────────────────────────────────────────────────
# This block only runs when you execute: python main.py
# In production / Docker, uvicorn is started directly via the CMD instruction.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
