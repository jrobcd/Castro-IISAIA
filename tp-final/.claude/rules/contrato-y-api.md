---
paths:
  - "backend/**"
  - "openapi.yaml"
  - "tests/**"
---

# Contrato y API

- El contrato va primero. Si una respuesta, un campo o un status code cambia, se cambia `openapi.yaml` antes que el código, y se sigue la skill `cambiar-contrato`.
- 404 es del path; 422 es del body. Un id del body que no existe es 422.
- Nada de reglas de Hanói en el servidor: ni "solo la de arriba" ni "no entra" ni "tres proyectos".
- Toda modificación de una tarea actualiza `updated_at`. Un PATCH sin campos es 422 y no toca nada.
- Los errores salen con `HTTPException(status, "mensaje en castellano")`. Nunca devolver `{ "detail": ... }`.
- No agregar `relationship` con cascada para "arreglar" el borrado de proyectos: el 409 con tareas pendientes es una decisión, no un bug.
- Los tests no levantan un cliente nuevo: usan el fixture `client`, que valida cada respuesta contra el contrato. Un test que esquiva ese fixture esquiva el contrato.
