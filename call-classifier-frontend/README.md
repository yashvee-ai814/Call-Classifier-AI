# Call Classifier — Frontend

A React + Vite single-page application that lets users paste a call transcript and instantly see an AI-generated classification from the backend.

---

## How it works

1. The user pastes a call transcript into the text area and clicks **Classify Call**.
2. The app sends a `POST /classify/` request to the backend API.
3. The backend returns a `reason` and `category`.
4. The result is displayed on screen.

---

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Node.js ≥ 18 | Runtime | [nodejs.org](https://nodejs.org/) |
| npm | Package manager | Bundled with Node.js |

The **backend** must also be running for classifications to work — see [call-classifier-backend/README.md](../call-classifier-backend/README.md).

---

## Running locally

```bash
# 1. Enter this directory
cd call-classifier-frontend

# 2. Install dependencies
npm install

# 3. Start the development server with hot-reload
npm run dev
```

The app will open at **http://localhost:5173**.

> The app talks to the backend at `http://localhost:8000` by default.  
> Make sure the backend is running before classifying transcripts.

---

## Running with Docker

```bash
# Build the image
docker build -t call-classifier-frontend .

# Run the container (maps container port 80 → host port 3000)
docker run -p 3000:80 call-classifier-frontend
```

Visit **http://localhost:3000**.

---

## Available scripts

| Command | What it does |
|---------|-------------|
| `npm run dev` | Start the Vite dev server with hot-reload |
| `npm run build` | Compile and bundle the app for production (output → `dist/`) |
| `npm run preview` | Serve the production build locally to test it |
| `npm run lint` | Run ESLint to check for code style issues |

---

## Project structure

```
call-classifier-frontend/
├── src/
│   ├── main.jsx     # React entry point — mounts the app into index.html
│   ├── App.jsx      # Root component — contains all the UI logic
│   ├── App.css      # Styles for the App component
│   └── index.css    # Global styles
├── public/          # Static assets copied as-is to the build output
├── index.html       # HTML shell — Vite injects the JS bundle here
├── vite.config.js   # Vite bundler configuration
├── nginx.conf       # nginx web server config (used in the Docker image)
└── Dockerfile       # Container build instructions
```
