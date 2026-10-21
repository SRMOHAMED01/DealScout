"""
main.py — Point d'entrée FastAPI pour DealScout (Palier F)

L'ajout du répertoire backend/ au sys.path permet aux imports internes
``app.xxx`` (utilisés dans tout le backend) de fonctionner quel que soit le
point d'entrée : ``uvicorn backend.app.main:app`` depuis la racine dealscout,
ou directement depuis le répertoire backend (workdir Docker /app).
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent  # .../dealscout/backend
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.models.company import Company
from app.models.investment_target import InvestmentTarget
from app.services.scoring_service import service

from app.routers import auth, companies, search

logger = logging.getLogger("dealscout.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialisation au démarrage et nettoyage à l'arrêt (FastAPI Lifespan).
    Crée les tables Postgres et synchronise les cibles scorées si Postgres est disponible.
    En cas d'indisponibilité du SGBD, bascule automatiquement sur le stockage Parquet.
    """
    try:
        Base.metadata.create_all(bind=engine)
        service.refresh_data()
        service.persist_to_postgres()
        logger.info("Base de données initialisée et cibles persistées")
    except Exception as exc:
        logger.warning(
            "Initialisation PostgreSQL reportée (mode fallback Parquet actif) : %s",
            exc,
        )
    yield


app = FastAPI(
    title="DealScout API — M&A Intelligence Platform",
    description="API for enterprise detection, financial analysis, multi-criteria screening, and M&A opportunity scoring.",
    version="1.0.0",
    lifespan=lifespan,
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
