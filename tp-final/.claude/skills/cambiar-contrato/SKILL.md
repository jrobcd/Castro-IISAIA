---
name: cambiar-contrato
description: Procedimiento para agregar o cambiar una operación, un campo o un status code de la API de Tareas en torre. Usar siempre que un cambio toque lo que entra o sale por /api.
---

# Cambiar el contrato

En este orden. No saltear pasos aunque el cambio parezca chico.

1. **Contrato.** Editar `openapi.yaml`. Subir la versión menor. Si es una operación nueva, el `operationId` va en camelCase y será el nombre de la función en `routes.py` y del método en `api.js`.
2. **Lint.** `npx @redocly/cli lint openapi.yaml`. Solo pueden quedar las advertencias ya justificadas en el README (`operation-4xx-response` en `GET /projects`).
3. **Test que falla.** Escribir en `tests/` el caso nuevo usando el fixture `client`. Correr `uv run pytest` y ver que falla por la razón correcta.
4. **Schemas.** `backend/schemas.py`: entrada y salida separadas. Entrada con `extra="forbid"` y `strict=True` (heredan de `Entrada`).
5. **Modelo.** Solo si hace falta una columna. Avisar que hay que borrar `tareas.db`: no hay migraciones.
6. **Ruta.** `backend/routes.py`. Errores con `HTTPException` y un mensaje en castellano.
7. **Verde.** `uv run pytest`. `test_contrato.py` falla si una operación del YAML no está implementada o si sobra una ruta.
8. **Cliente.** Si la interfaz lo va a usar: el método en `frontend/js/api.js`, con el mismo nombre que el `operationId`.
9. **Navegador.** Levantar el servidor con la base vacía y correr `scripts/recorrido_navegador.py`.
10. **Informe.** Si el cambio contradice una decisión del README, actualizar esa sección en el mismo commit.
