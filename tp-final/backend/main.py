"""La app: un solo proceso sirve la API bajo /api y el frontend desde /."""

from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend import errores
from backend.db import Base, engine
from backend.routes import router

RAIZ = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)
errores.registrar(app)
app.include_router(router, prefix="/api")

# /docs muestra el contrato escrito a mano, no uno generado desde el código.
# Que coincidan lo comprueba tests/test_contrato.py.
_contrato = yaml.safe_load((RAIZ / "openapi.yaml").read_text(encoding="utf-8"))
app.openapi = lambda: _contrato

# Último: el mount en "/" atrapa todo lo que se registre después.
app.mount("/", StaticFiles(directory=RAIZ / "frontend", html=True), name="frontend")
