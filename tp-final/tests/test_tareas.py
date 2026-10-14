import pytest

from tests.conftest import fecha


def test_crear_en_proyecto(client, proyecto):
    r = client.post(f"/api/projects/{proyecto['id']}/tasks", json={"title": "Informe", "priority": 5})
    assert r.status_code == 201
    t = r.json()
    assert t["projectId"] == proyecto["id"] and t["done"] is False
    assert r.headers["location"] == f"/api/tasks/{t['id']}"


def test_crear_en_proyecto_inexistente_es_404(client):
    r = client.post("/api/projects/99/tasks", json={"title": "x", "priority": 1})
    assert r.status_code == 404


def test_listar_proyecto_inexistente_es_404_no_lista_vacia(client):
    assert client.get("/api/projects/99/tasks").status_code == 404


def test_filtrar_por_done(client, proyecto, tarea):
    client.post(f"/api/projects/{proyecto['id']}/tasks", json={"title": "Otra", "priority": 1})
    client.patch(f"/api/tasks/{tarea['id']}", json={"done": True})
    base = f"/api/projects/{proyecto['id']}/tasks"
    assert [t["id"] for t in client.get(base, params={"done": "true"}).json()] == [tarea["id"]]
    assert len(client.get(base, params={"done": "false"}).json()) == 1
    assert len(client.get(base).json()) == 2


@pytest.mark.parametrize("cuerpo, mensaje", [
    ({"title": "x"}, "Falta el campo priority."),
    ({"title": "x", "priority": 6}, "La prioridad va de 1 a 5."),
    ({"title": "x", "priority": "3"}, "priority tiene que ser un entero."),
    ({"title": "", "priority": 3}, "title no puede estar vacío."),
    ({"title": "x" * 121, "priority": 3}, "title admite hasta 120 caracteres."),
])
def test_validaciones_de_creacion(client, proyecto, cuerpo, mensaje):
    r = client.post(f"/api/projects/{proyecto['id']}/tasks", json=cuerpo)
    assert r.status_code == 422
    assert r.json() == {"status": 422, "message": mensaje}


def test_mover_cambia_proyecto_y_updated_at(client, tarea):
    destino = client.post("/api/projects", json={"name": "Casa"}).json()
    r = client.patch(f"/api/tasks/{tarea['id']}", json={"projectId": destino["id"]})
    assert r.status_code == 200
    assert r.json()["projectId"] == destino["id"]
    assert fecha(r.json()["updatedAt"]) > fecha(tarea["updatedAt"])


def test_null_explicito_es_422(client, tarea):
    assert client.patch(f"/api/tasks/{tarea['id']}", json={"title": None}).status_code == 422


def test_tarea_inexistente_es_404(client):
    for metodo in ("get", "delete"):
        r = getattr(client, metodo)("/api/tasks/99")
        assert r.status_code == 404 and r.json()["message"] == "La tarea no existe."


def test_borrar(client, tarea):
    assert client.delete(f"/api/tasks/{tarea['id']}").status_code == 204
    assert client.get(f"/api/tasks/{tarea['id']}").status_code == 404


# --- Las tres deudas que dejó anotadas el TP 2 ---------------------------------

def test_deuda_1_proyecto_destino_inexistente_es_422_no_404(client, tarea):
    r = client.patch(f"/api/tasks/{tarea['id']}", json={"projectId": 99})
    assert r.status_code == 422
    assert r.json()["message"] == "El proyecto destino no existe."


def test_deuda_2_patch_vacio_es_422_y_no_toca_updated_at(client, tarea):
    r = client.patch(f"/api/tasks/{tarea['id']}", json={})
    assert r.status_code == 422
    assert client.get(f"/api/tasks/{tarea['id']}").json()["updatedAt"] == tarea["updatedAt"]


def test_deuda_3_campo_desconocido_es_422(client, proyecto):
    r = client.post(f"/api/projects/{proyecto['id']}/tasks",
                    json={"title": "x", "priority": 1, "projectId": proyecto["id"]})
    assert r.status_code == 422
    assert r.json()["message"] == "Campo desconocido: projectId."
