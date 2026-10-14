from tests.conftest import fecha

def test_crear_devuelve_201_con_location(client):
    r = client.post("/api/projects", json={"name": "  Facultad  "})
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["name"] == "Facultad"
    assert r.headers["location"] == f"/api/projects/{cuerpo['id']}"
    assert cuerpo["createdAt"].endswith("Z") and cuerpo["createdAt"] == cuerpo["updatedAt"]


def test_nombre_vacio_es_422(client):
    r = client.post("/api/projects", json={"name": "   "})
    assert r.status_code == 422
    assert r.json() == {"status": 422, "message": "name no puede estar vacío."}


def test_listar(client, proyecto):
    assert [p["id"] for p in client.get("/api/projects").json()] == [proyecto["id"]]


def test_ver_inexistente_es_404(client):
    r = client.get("/api/projects/99")
    assert r.status_code == 404
    assert r.json() == {"status": 404, "message": "El proyecto no existe."}


def test_id_no_entero_es_404(client):
    assert client.get("/api/projects/abc").status_code == 404


def test_renombrar_actualiza_updated_at(client, proyecto):
    r = client.patch(f"/api/projects/{proyecto['id']}", json={"name": "Tesis"})
    assert r.status_code == 200
    assert r.json()["name"] == "Tesis"
    assert fecha(r.json()["updatedAt"]) > fecha(proyecto["updatedAt"])


def test_borrar_con_pendientes_es_409(client, proyecto, tarea):
    r = client.delete(f"/api/projects/{proyecto['id']}")
    assert r.status_code == 409
    assert r.json()["message"] == "El proyecto tiene tareas pendientes."


def test_borrar_con_solo_hechas_las_borra(client, proyecto, tarea):
    client.patch(f"/api/tasks/{tarea['id']}", json={"done": True})
    r = client.delete(f"/api/projects/{proyecto['id']}")
    assert r.status_code == 204 and r.content == b""
    assert client.get(f"/api/tasks/{tarea['id']}").status_code == 404
