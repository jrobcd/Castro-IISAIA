"""Base temporal: se fija DATABASE_URL antes de importar la app, así nunca toca tareas.db."""

import os
from datetime import datetime
import tempfile
from pathlib import Path

import pytest

_TMP = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}"

from fastapi.testclient import TestClient  # noqa: E402

from backend.db import Base, engine  # noqa: E402
from backend.main import app  # noqa: E402
from tests.contrato import verificar  # noqa: E402


class ClienteContrato(TestClient):
    """Toda respuesta de /api que pasa por acá se valida contra openapi.yaml."""

    def request(self, method, url, *args, **kwargs):
        respuesta = super().request(method, url, *args, **kwargs)
        verificar(method, str(url), respuesta)
        return respuesta


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with ClienteContrato(app) as c:
        yield c


def fecha(texto: str) -> datetime:
    """Las fechas se comparan como fechas: como texto, "...:00Z" queda después de "...:00.5Z"."""
    return datetime.fromisoformat(texto)


@pytest.fixture
def proyecto(client):
    return client.post("/api/projects", json={"name": "Facultad"}).json()


@pytest.fixture
def tarea(client, proyecto):
    r = client.post(f"/api/projects/{proyecto['id']}/tasks", json={"title": "Leer el paper", "priority": 3})
    return r.json()
