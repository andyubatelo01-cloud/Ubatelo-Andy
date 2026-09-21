"""Point d'entrée FastAPI du Bureau du Pasteur."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from . import audit
from .api import auth, campaigns, events, members, office, validation, webhooks
from .config import get_settings
from .db import SessionLocal, init_db
from .models import Role, User
from .security import hash_password
from .services.members import ensure_default_groups
from .services.scheduling import SchedulerThread

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("bureau")
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def bootstrap() -> None:
    """Crée les tables, les groupes par défaut et le compte administrateur initial."""
    init_db()
    s = get_settings()
    db = SessionLocal()
    try:
        ensure_default_groups(db)
        if db.scalar(select(User).where(User.role == Role.PASTEUR.value)) is None:
            db.add(User(email=s.admin_email.lower(), name=s.admin_name, password_hash=hash_password(s.admin_password), role=Role.PASTEUR.value, phone=s.pastor_phone))
            audit.log(db, "SYSTEME", "ADMIN_BOOTSTRAPPED", "user", s.admin_email)
            if s.admin_password == "changez-moi":
                logger.warning("Le mot de passe administrateur par défaut est utilisé : changez ADMIN_PASSWORD.")
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap()
    scheduler = None
    if get_settings().scheduler_enabled:
        scheduler = SchedulerThread(SessionLocal)
        scheduler.start()
    app.state.scheduler = scheduler
    yield
    if scheduler:
        scheduler.stop()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title=s.app_name, version="1.0.0", description="Bureau d'IA de gestion et de communication pastorale. L'IA prépare, le pasteur valide, le système envoie.", lifespan=lifespan, docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")

    for r in (auth.router, members.router, events.router, campaigns.router, validation.router, office.router, webhooks.router):
        app.include_router(r)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):  # pragma: no cover
        logger.exception("Erreur non gérée sur %s", request.url.path)
        return JSONResponse({"detail": "Erreur interne. L'incident a été journalisé."}, status_code=500)

    @app.get("/api/sante", tags=["bureau"])
    def health():
        return {"ok": True, "application": s.app_name, "environnement": s.app_env}

    if FRONTEND.exists():
        app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

        @app.get("/", include_in_schema=False)
        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str = ""):
            if path.startswith(("api/", "webhooks/", "valider/")):
                return JSONResponse({"detail": "Introuvable"}, status_code=404)
            target = FRONTEND / path
            if path and target.is_file():
                return FileResponse(target)
            return FileResponse(FRONTEND / "index.html")

    return app


app = create_app()
