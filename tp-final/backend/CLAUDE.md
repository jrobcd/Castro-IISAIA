# backend/

## Capas

`db.py` (engine, `PRAGMA foreign_keys`, sesión por request) → `models.py` (tablas `Project` y `Task`, en snake_case) → `schemas.py` (entrada y salida, en camelCase, separadas de las tablas) → `routes.py` (las 10 operaciones) → `errores.py` (todo error sale como `{ status, message }`) → `main.py` (app, tablas, contrato en `/docs`, estáticos).

## Recorrido de un request

`PATCH /api/tasks/7 {"projectId": 3}`:

1. `TaskPatch` valida en modo estricto, con `extra="forbid"`. Si el body está vacío, es 422 (`_no_vacio`).
2. `updateTask` busca la tarea (404 si no existe) y el proyecto destino (422 si no existe: está en el body, no en el path).
3. Aplica solo `model_fields_set`, actualiza `updated_at` y hace commit.
4. `TaskOut` serializa en camelCase y estampa UTC en las fechas, porque SQLite las devuelve sin zona.

## Errores

- **`RequestValidationError`:** si el error está en el path (un id que no es entero), responde 404. Si está en el body, 422, con un mensaje en castellano que arma `_mensaje`.
- **`HTTPException` bajo `/api/`:** responde `{ status, message }`. Fuera de `/api/` usa el handler por defecto, que es el de los estáticos.

## Cambiar el esquema

No hay migraciones: `create_all` crea las tablas que faltan, pero no altera las que ya existen. Si cambia una columna, hay que borrar `tareas.db`. Antes de tocar `models.py`, seguí la skill `cambiar-contrato`: un campo nuevo en la tabla casi siempre es un campo nuevo en el contrato.

## Probar

```bash
uv run pytest                     # usa una base temporal (tests/conftest.py fija DATABASE_URL antes de importar)
curl -i -X PATCH 127.0.0.1:8000/api/tasks/1 -H 'Content-Type: application/json' -d '{}'
```
