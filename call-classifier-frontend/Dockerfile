# ─────────────────────────────────────────────────────────────────────────────
# Call Classifier Frontend — Dockerfile
#
# Uses a two-stage build:
#   Stage 1 (build): installs Node dependencies and compiles the React app
#   Stage 2 (serve): copies only the compiled static files into a tiny nginx
#                    image — no Node.js, no source code, no dev dependencies
#
# To build:  docker build -t call-classifier-frontend .
# To run:    docker run -p 3000:80 call-classifier-frontend
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Node build ────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests first so Docker can cache the npm install layer.
# This layer is only invalidated when package.json or package-lock.json changes.
COPY package.json package-lock.json ./

# `npm ci` is like `npm install` but:
#   - Uses package-lock.json exactly (deterministic, no surprise upgrades)
#   - Deletes node_modules first to ensure a clean install
RUN npm ci

# Copy the rest of the source code and build the production bundle.
# Vite outputs optimised, minified files into the /app/dist directory.
COPY . .
RUN npm run build

# ── Stage 2: nginx static file server ─────────────────────────────────────────
# nginx:alpine is a tiny (~5 MB) web server image — perfect for serving
# pre-built static files. It has no Node.js, keeping the image minimal and secure.
FROM nginx:alpine

# Copy the compiled app from the builder stage into nginx's web root
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy our custom nginx config (handles SPA routing and caching)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# nginx listens on port 80 by default
EXPOSE 80

# Health check: verify the index page is being served
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/index.html || exit 1

# Start nginx in the foreground (required for Docker — it must stay in the
# foreground so Docker knows the container is still running)
CMD ["nginx", "-g", "daemon off;"]