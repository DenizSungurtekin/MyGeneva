from __future__ import annotations

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


def create_app() -> FastAPI:
    app = FastAPI(
        title="MyGeneva API",
        description="Backend API for MyGeneva — aggregation of events and restaurants in Geneva.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
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

    return app


app = create_app()
