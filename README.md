# Call-Classifier-AI

A full-stack AI application that classifies the intent of customer call transcripts using a locally-hosted large language model via [Ollama](https://ollama.com). Built with a **React + Vite** frontend and a **FastAPI** backend, and fully containerised with Docker.

---

## Overview

Call-Classifier-AI takes a raw call transcript as input and returns a structured classification:

| Field | Description |
|---|---|
| `reason` | A concise, human-readable summary of why the call was made |
| `category` | One of: `inquiry`, `advice_request`, `complaint`, `account_status`, `transaction`, `other` |

The LLM prompt is tuned for **investment, wealth, and retirement** domain calls (e.g. Aviva products), but can be adapted to any industry.

---

## Architecture

```
┌─────────────────────┐        POST /classify/        ┌──────────────────────────┐
│  React Frontend     │ ─────────────────────────────▶ │  FastAPI Backend         │
│  (Vite, port 3000)  │ ◀───────────────────────────── │  (Uvicorn, port 8000)    │
└─────────────────────┘    { reason, category }        └────────────┬─────────────┘
                                                                     │  Ollama HTTP API
                                                                     ▼
                                                        ┌──────────────────────────┐
                                                        │  Ollama (LLM runtime)    │
                                                        │  (port 11434)            │
                                                        └──────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 5 |
| Backend | FastAPI, Python 3.11, Uvicorn |
| Package manager | [uv](https://github.com/astral-sh/uv) |
| LLM runtime | [Ollama](https://ollama.com) |
| HTTP client | HTTPX |
| Data validation | Pydantic v2 |
| Containerisation | Docker (multi-stage builds) |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) — for containerised setup
- **Or**, for local development:
  - Python ≥ 3.11
  - [uv](https://github.com/astral-sh/uv) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Node.js ≥ 20
  - [Ollama](https://ollama.com/download) installed and running

---

## Quickstart

### 1. Start Ollama and pull a model

```bash
ollama serve                        # starts the Ollama server on port 11434
ollama pull gpt-oss:120b-cloud      # default model used by the backend
```

You can use any instruction-following model. See [Configuration](#configuration) to change the model.

---

### 2a. Run with Docker

Build and start each service in its own container:

```bash
# Backend
cd call-classifier-backend
docker build -t call-classifier-backend .
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  call-classifier-backend

# Frontend (in a new terminal)
cd call-classifier-frontend
docker build -t call-classifier-frontend .
docker run -p 3000:80 call-classifier-frontend
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 2b. Run locally (without Docker)

**Backend:**

```bash
cd call-classifier-backend
uv sync                             # creates .venv and installs dependencies
uv run uvicorn main:app --reload    # starts on http://localhost:8000
```

**Frontend:**

```bash
cd call-classifier-frontend
npm install
npm run dev                         # starts on http://localhost:5173
```

---

## API Reference

Interactive docs are available at [http://localhost:8000/docs](http://localhost:8000/docs) when the backend is running.

### `POST /classify/`

Classifies a call transcript.

**Request body:**

```json
{
  "transcript": "Hello, I'd like to check the current value of my pension pot."
}
```

**Response:**

```json
{
  "reason": "Customer is requesting the current value of their pension account.",
  "category": "account_status"
}
```

**Category values:**

| Value | Meaning |
|---|---|
| `inquiry` | General question or information request |
| `advice_request` | Customer seeking financial/product advice |
| `complaint` | Customer expressing dissatisfaction |
| `account_status` | Checking balances, statements, or policy status |
| `transaction` | Requesting a financial transaction or change |
| `other` | Does not fit any of the above |

---

## Configuration

The backend reads the following environment variables:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | URL of the running Ollama server |
| `OLLAMA_MODEL` | `gpt-oss:120b-cloud` | Ollama model to use for classification |

Set them at runtime:

```bash
# Local
export OLLAMA_MODEL=llama3
uv run uvicorn main:app --reload

# Docker
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -e OLLAMA_MODEL=llama3 \
  call-classifier-backend
```

---

## Project Structure

```
Call-Classifier-AI/
├── call-classifier-backend/
│   ├── main.py           # FastAPI app entry point
│   ├── middleware.py     # CORS middleware
│   ├── models.py         # Pydantic request / response models
│   ├── pyproject.toml    # Python project config (uv)
│   ├── Dockerfile        # Multi-stage Docker build
│   └── routers/
│       └── llm.py        # /classify endpoint + Ollama integration
└── call-classifier-frontend/
    ├── src/
    │   ├── App.jsx       # Main UI component
    │   └── main.jsx      # React entry point
    ├── package.json
    ├── vite.config.js
    └── Dockerfile        # Multi-stage Docker build (nginx)
```

---

## License

[MIT](LICENSE)
