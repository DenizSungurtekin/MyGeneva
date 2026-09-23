from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import events, favorites, restaurants


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
    app.include_router(restaurants.router)
    app.include_router(favorites.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
