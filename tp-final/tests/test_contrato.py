"""El contrato y el código no pueden divergir en qué operaciones existen."""

from fastapi.routing import APIRoute

from backend.routes import router
from tests.contrato import operaciones


def _rutas_api():
    # Se recorre el router y no app.routes: desde FastAPI 0.14x un router incluido
    # queda envuelto en un objeto privado y sus rutas no aparecen en app.routes.
    return {
        (metodo.lower(), r.path): r.name
        for r in router.routes
        if isinstance(r, APIRoute)
        for metodo in r.methods
    }


def test_toda_operacion_del_contrato_esta_implementada_con_su_operation_id():
    rutas = _rutas_api()
    for metodo, path, op in operaciones():
        assert (metodo, path) in rutas, f"falta {metodo.upper()} {path}"
        assert rutas[(metodo, path)] == op["operationId"]


def test_no_hay_rutas_fuera_del_contrato():
    documentadas = {(m, p) for m, p, _ in operaciones()}
    assert set(_rutas_api()) <= documentadas


def test_docs_sirve_el_contrato_escrito_a_mano(client):
    assert client.get("/openapi.json").json()["info"]["title"].startswith("Tareas en torre")
