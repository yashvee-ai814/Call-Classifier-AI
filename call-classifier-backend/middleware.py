# middleware.py
#
# Middleware is code that runs on EVERY request, before it reaches a route handler.
# Think of it as a gatekeeper or filter sitting between the client and your endpoints.
#
# This file sets up CORS (Cross-Origin Resource Sharing).
# CORS is a browser security feature that blocks requests coming from a different
# "origin" (domain + port) than your API. For example, a React app on
# http://localhost:5173 calling an API on http://localhost:8000 is a cross-origin
# request. Without CORS configured, the browser will reject it.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def add_middleware(app: FastAPI) -> None:
    """
    Register all middleware on the FastAPI app instance.
    Call this function once in main.py before the app starts.
    """

    # CORSMiddleware handles the preflight OPTIONS requests and adds the right
    # response headers so the browser allows the cross-origin call.
    app.add_middleware(
        CORSMiddleware,
        # allow_origins: which frontend URLs are allowed to call this API.
        # "*" means anyone — fine for development, but in production you should
        # list only your real frontend URL, e.g. ["https://yourapp.com"]
        allow_origins=["*"],
        # allow_credentials: lets the browser send cookies / auth headers
        allow_credentials=True,
        # allow_methods: which HTTP methods are permitted (GET, POST, etc.)
        allow_methods=["*"],
        # allow_headers: which request headers the browser can send
        allow_headers=["*"],
    )
