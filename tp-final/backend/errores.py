"""Todo error de la API sale con la forma del contrato: { status, message }, en castellano."""

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

RECURSO_DEL_PATH = {"projectId": "El proyecto no existe.", "taskId": "La tarea no existe."}


def error(status: int, message: str) -> JSONResponse:
    return JSONResponse({"status": status, "message": message}, status_code=status)


def _mensaje(e: dict) -> str:
    campo = str(e["loc"][-1]) if e["loc"] else "cuerpo"
    tipo, ctx = e["type"], e.get("ctx", {})
    if tipo == "missing":
        return "Falta el cuerpo." if campo == "body" else f"Falta el campo {campo}."
    if tipo == "extra_forbidden":
        return f"Campo desconocido: {campo}."
    if tipo == "string_too_short":
        return f"{campo} no puede estar vacío."
    if tipo == "string_too_long":
        return f"{campo} admite hasta {ctx.get('max_length')} caracteres."
    if tipo in ("greater_than_equal", "less_than_equal"):
        return "La prioridad va de 1 a 5." if campo == "priority" else f"{campo} está fuera de rango."
    if tipo in ("int_type", "int_parsing"):
        return f"{campo} tiene que ser un entero."
    if tipo == "string_type":
        return f"{campo} tiene que ser texto."
    if tipo == "bool_type":
        return f"{campo} tiene que ser booleano."
    if tipo == "json_invalid":
        return "El cuerpo no es JSON válido."
    if tipo == "value_error":
        return str(ctx.get("error", e["msg"]))
    return f"{campo}: valor inválido."


def registrar(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def _validacion(_request: Request, exc: RequestValidationError):
        errores = exc.errors()
        # 404 es del path: un id que ni siquiera es entero no puede existir.
        for e in errores:
            if e["loc"] and e["loc"][0] == "path":
                return error(404, RECURSO_DEL_PATH.get(e["loc"][-1], "No existe."))
        return error(422, _mensaje(errores[0]))

    @app.exception_handler(HTTPException)
    async def _http(request: Request, exc: HTTPException):
        if request.url.path.startswith("/api/"):
            return error(exc.status_code, str(exc.detail))
        return await http_exception_handler(request, exc)
