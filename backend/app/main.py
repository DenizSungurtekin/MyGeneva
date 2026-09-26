from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the sibling `pipeline` package importable from the backend process —
# used by /places/{id}/refresh which reuses the enricher code.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import events, favorites, places, restaurants


APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    app = FastAPI(
        title="MyGeneva API",
        description="Backend API for MyGeneva — aggregation of events and restaurants in Geneva.",
        version=APP_VERSION,
    )

    # No cookie-based auth today → allow_credentials must be False when we
    # use a wildcard. Configured origins keep credentials=True in case we
    # add sessions later; wildcard falls back to no-credentials.
    configured_origins = list(settings.cors_origins or [])
    if configured_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=configured_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(events.router)
    app.include_router(places.router)
    app.include_router(restaurants.router)
    app.include_router(favorites.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/version", tags=["meta"])
    def version() -> dict:
        """Report the running app version + the commit SHA if the deployer
        exposed it via env (Railway exposes RAILWAY_GIT_COMMIT_SHA)."""
        return {
            "version": APP_VERSION,
            "commit": os.environ.get("RAILWAY_GIT_COMMIT_SHA", "unknown"),
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "local"),
        }

    return app


app = create_app()
