"""Valida respuestas reales contra openapi.yaml, que es el contrato del TP 2."""

import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

CONTRATO = yaml.safe_load((Path(__file__).parent.parent / "openapi.yaml").read_text(encoding="utf-8"))
PREFIJO = "/api"
METODOS = ("get", "post", "put", "patch", "delete")

_URI = "urn:contrato"
_registro = Registry().with_resource(_URI, Resource.from_contents(CONTRATO, default_specification=DRAFT202012))


def _resolver(nodo: dict) -> dict:
    """Sigue un $ref local (#/components/...) hasta el objeto."""
    while "$ref" in nodo:
        objetivo = CONTRATO
        for parte in nodo["$ref"].removeprefix("#/").split("/"):
            objetivo = objetivo[parte]
        nodo = objetivo
    return nodo


def operaciones():
    """(método, path del contrato, operación) para cada operación del YAML."""
    for path, item in CONTRATO["paths"].items():
        for metodo in METODOS:
            if metodo in item:
                yield metodo, path, item[metodo]


def _buscar(metodo: str, path_real: str):
    for m, path, op in operaciones():
        patron = "^" + re.sub(r"\{[^}]+\}", "[^/]+", path) + "$"
        if m == metodo and re.match(patron, path_real):
            return path, op
    return None, None


def verificar(metodo: str, url: str, respuesta) -> None:
    """Falla si la respuesta no está permitida por el contrato."""
    path_real = url.split("?")[0]
    if not path_real.startswith(PREFIJO + "/"):
        return
    path, op = _buscar(metodo.lower(), path_real.removeprefix(PREFIJO))
    assert op is not None, f"{metodo} {path_real} no está en el contrato"
    status = str(respuesta.status_code)
    assert status in op["responses"], f"{metodo} {path} respondió {status}, que el contrato no documenta"
    doc = _resolver(op["responses"][status])

    for header in doc.get("headers", {}):
        assert header.lower() in respuesta.headers, f"{metodo} {path} {status}: falta el header {header}"

    contenido = doc.get("content", {}).get("application/json")
    if contenido is None:
        assert respuesta.content == b"", f"{metodo} {path} {status}: el contrato no documenta cuerpo"
        return
    esquema = {"$ref": f"{_URI}#{_puntero(contenido['schema'])}"} if "$ref" in contenido["schema"] else contenido["schema"]
    validador = Draft202012Validator(_con_uri(esquema), registry=_registro)
    errores = sorted(validador.iter_errors(respuesta.json()), key=str)
    assert not errores, f"{metodo} {path} {status}: {errores[0].message}"


def _puntero(nodo: dict) -> str:
    return nodo["$ref"].removeprefix("#")


def _con_uri(esquema):
    """Los $ref internos de un schema inline también tienen que resolverse contra el contrato."""
    if isinstance(esquema, dict):
        return {k: (f"{_URI}{v}" if k == "$ref" and v.startswith("#") else _con_uri(v)) for k, v in esquema.items()}
    if isinstance(esquema, list):
        return [_con_uri(v) for v in esquema]
    return esquema
