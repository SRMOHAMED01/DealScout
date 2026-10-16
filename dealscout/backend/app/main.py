"""
main.py â€” Point d'entrÃ©e FastAPI pour DealScout (Palier F)
"""

from __future__ import annotations

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, companies, search

logger = logging.getLogger("dealscout.backend")

app = FastAPI(
    title="DealScout API — M&A Intelligence Platform",
    description="API for enterprise detection, financial analysis, multi-criteria screening, and M&A opportunity scoring.",
    version="1.0.0",
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(search.router)


@app.get("/health", tags=["Health"])
def health_check():
    """Service health and readiness check."""
    return {
        "status": "healthy",
        "service": "dealscout-api",
        "version": "1.0.0",
    }


# Prometheus instrumentation (Palier H)
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except Exception as prom_err:
    logger.warning("Prometheus instrumentation skipped: %s", prom_err)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

