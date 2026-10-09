# Registro de prompts — TP 2

Herramienta: Claude Code, en una sola sesión, con el repositorio abierto, así que el modelo podía leer `tp1/index.html`. Los prompts van tal como se enviaron. Debajo de cada uno, en cursiva, anoto qué hice con la respuesta.

---

## Prompt 1

```
Contexto: TP 2. Consigna: un openapi.yaml de una API REST de proyectos y
tareas, sin implementación. Es el contrato del backend del TP 1
(tp1/index.html, objeto `api`). El final va a conectar los dos, así que el
contrato tiene que servirle a ese front tal como está.

Recursos (los mismos del TP 1, con updatedAt, que el TP 1 necesita para
ordenar las pilas):
- Project { id, name, createdAt, updatedAt }
- Task    { id, projectId, title, priority (1–5), done, createdAt, updatedAt }

Endpoints:
- /projects                    GET, POST
- /projects/{projectId}        GET, PATCH, DELETE
- /projects/{projectId}/tasks  GET, POST
- /tasks/{taskId}              GET, PATCH, DELETE

Decisiones ya tomadas (respetalas; si te parece que alguna está mal, decímelo
antes de escribir el yaml, no la cambies en silencio):
- Las tareas se crean y se listan bajo su proyecto, pero se leen, modifican y
  borran por su propio id: para operar una tarea no hace falta saber en qué
  proyecto está.
- Mover una tarea es PATCH /tasks/{taskId} con projectId en el body.
- Schemas de entrada y de salida separados. id, createdAt y updatedAt los
  genera el servidor. El POST anidado NO lleva projectId en el body: ya está
  en el path.
- PATCH es parcial. Body vacío o con campos desconocidos → 422.
- Un único schema Error con la misma forma que los rechazos del TP 1:
  { status, message }.
- 404 solo cuando no existe el recurso del path. Un projectId inexistente en
  el body es un dato inválido → 422.
- DELETE de un proyecto con tareas pendientes → 409. Con solo tareas hechas,
  se borra con ellas.
- DELETE → 204 sin cuerpo. POST → 201 con Location.
- GET /projects/{projectId}/tasks acepta ?done=true|false. Si el proyecto no
  existe → 404, no [].
- Ninguna regla de Hanói en el contrato.

Forma: OpenAPI 3.1, operationId iguales a los nombres de los métodos de `api`
en el TP 1, descripciones y ejemplos en español, componentes reutilizables
para parámetros y respuestas de error.
```

*El modelo no objetó ninguna decisión. Pasé el YAML por `redocly lint`: era válido, pero tenía 10 errores de `security-defined` y 5 advertencias.*

---

## Prompt 2

```
Dos revisiones, en este orden.

1. Contrastá el yaml contra el objeto `api` de tp1/index.html, método por
   método: operationId, códigos de estado, validaciones y campos. Para cada
   diferencia, decidí quién tiene razón. Si es el yaml, corregilo. Si es el
   TP 1, NO lo toques (ya está entregado): anotalo como deuda para el final.

2. Corré `npx @redocly/cli lint tp2/openapi.yaml`. Cada hallazgo se resuelve
   o se justifica; no quiero un ignore file que lo tape todo.
```

*La comparación encontró cuatro diferencias: en tres tenía razón el contrato y en una el YAML estaba mal. Del linter resolví los errores y dejé dos advertencias justificadas. Todo eso está en el README.*
