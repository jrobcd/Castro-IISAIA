# CLAUDE.md

Guía para Claude Code al trabajar en este directorio.

## Qué es este proyecto

Tareas en torre, versión con servidor. Es la interfaz Bad UI del TP 1 (cada proyecto es una torre de Hanói y cada tarea un disco) sobre una implementación en FastAPI + SQLite del contrato del TP 2. Un solo proceso sirve la API bajo `/api` y el frontend desde `/`.

Vive en `tp-final/`, al lado de `tp1/` y `tp2/`. Esas dos carpetas son entregas cerradas: **no se tocan**. El `README.md` de acá es el informe del TP, no un manual de uso. Si un cambio invalida una decisión o un bug que se cuenta ahí, hay que actualizar esa sección en el mismo commit.

`docs/plan.md` es el plan original, **congelado a propósito**. No se actualiza para "sincronizarlo": las diferencias se explican en el README.

## Comandos

```bash
uv sync                                          # dependencias
uv run fastapi dev backend/main.py               # app en http://127.0.0.1:8000, contrato en /docs
uv run pytest                                    # API + contrato, con base temporal
uv run --group e2e python scripts/recorrido_navegador.py http://127.0.0.1:8000/   # con el servidor levantado y la base vacía
```

`tareas.db` se crea al arrancar. Para empezar de cero, se borra el archivo. Las tres torres no las siembra el servidor: las crea la interfaz la primera vez que encuentra menos de tres proyectos.

## Dónde seguir leyendo

| Archivo | Qué cubre |
|---------|-----------|
| `backend/CLAUDE.md` | capas, recorrido de un request, errores, cómo cambiar el esquema |
| `frontend/CLAUDE.md` | módulos, quién llama a quién, dónde viven las reglas de Hanói |
| `.claude/rules/contrato-y-api.md` | qué hacer y qué no al tocar la API |
| `.claude/rules/interfaz-hanoi.md` | qué hacer y qué no al tocar la interfaz |
| `.claude/skills/cambiar-contrato/` | el procedimiento completo para cambiar la API, en orden |
| `.claude/agents/explorador.md` | sub-agente de solo lectura para preguntas que cruzan las dos mitades |

Comandos: `/explicar <archivo>` y `/pre-entrega`.

## Los tres contratos que sostienen el diseño

1. **`openapi.yaml` manda.** Es la copia del contrato del TP 2 (v1.1, con `servers` y `Location` adaptados). `/docs` muestra ese archivo, no uno generado desde el código. Cada respuesta que pasa por el `client` de pytest se valida contra él (`tests/contrato.py`), y `test_contrato.py` comprueba que toda operación esté implementada con su `operationId` como nombre de función. Un cambio en la API empieza por el YAML.
2. **Las reglas de Hanói viven solo en la interfaz.** El servidor acepta cualquier movimiento válido como dato. "No entra", "solo la de arriba" y "tres torres" están en `frontend/js/torres.js` y `app.js`.
3. **Un solo archivo habla con el servidor.** Es `frontend/js/api.js`, con los mismos métodos y firmas que el objeto `api` del TP 1. Rechaza siempre con `{ status, message }`.

## Trampas ya pagadas

- **El orden de la pila depende de `updatedAt`.** Toda modificación de una tarea tiene que actualizarlo, la mudanza incluida. Un PATCH vacío no puede tocarlo: es 422.
- **Comparar fechas como fechas.** El servidor omite los microsegundos cuando valen cero, y como texto `"…:00Z"` queda después de `"…:00.5Z"`. `torres.js` usa `Date.parse`.
- **Borrar un proyecto: primero las tareas, en una sentencia propia.** Los modelos no declaran `relationship`, así que el unit of work de SQLAlchemy no sabe el orden y viola la foreign key (que está activada con un `PRAGMA`).
- **Routers incluidos.** En FastAPI 0.14x `app.routes` no lista las rutas de un router incluido. Para recorrerlas, usar `backend.routes.router.routes`.
- **Selección entre pestañas.** Una tarea levantada se suelta si al recargar ya no está arriba **de la torre de la que salió**. Otra pestaña puede haberla mudado.

## Convenciones

- Archivos de menos de 300 líneas, funciones de menos de 50.
- Todo en castellano: UI, comentarios, mensajes de error y commits (`tipo: descripción en minúscula`). Excepción: los nombres del contrato (`projectId`, `updatedAt`, `operationId`) quedan como en el TP 2.
- Un commit por pieza que funciona y se puede probar.
