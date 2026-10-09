# TP 2 — Contrato de Tareas en torre

Un [openapi.yaml](openapi.yaml) que describe la API REST de proyectos y tareas detrás de la interfaz del TP 1. Cuatro paths, diez operaciones, sin nada implementado: el entregable es el contrato.

## Qué construí

El contrato limpio de un sistema cuya interfaz es deliberadamente hostil. En el TP 1, cada proyecto es una torre de Hanói y solo se toca la tarea de arriba. Acá no queda nada de eso. Una tarea se puede mover a cualquier proyecto, cambiar de prioridad o borrar, y la API no pregunta qué hay encima. La broma es de la interfaz; el contrato no la conoce.

Ya hay un cliente escrito contra este contrato: el objeto `api` del TP 1, que hoy guarda en `localStorage`. Los `operationId` tienen los mismos nombres que sus métodos (`listTasks`, `updateTask`…), y el schema `Error` tiene la misma forma que sus rechazos (`{ status, message }`). En el final, ese objeto pasa a llamar a esta API con `fetch`.

## Cómo lo dirigí

Dos prompts, en una sola sesión de Claude Code con el repositorio abierto. El primero llega con las decisiones ya tomadas y le pide al modelo que me avise antes de cambiar alguna. El segundo es de revisión: contrastar el contrato contra el cliente del TP 1 y pasar un linter. No le pedí que diseñara la API: le pedí que escribiera la que yo ya había diseñado y que encontrara dónde no cerraba.

## Decisiones que tomé yo

**Crear y listar anidado, operar por id propio.** `POST /projects/{projectId}/tasks` y `GET /projects/{projectId}/tasks`, pero `GET`, `PATCH` y `DELETE` sobre `/tasks/{taskId}`. La pertenencia importa al nacer y al listar: una tarea no existe sin proyecto. Para operar una tarea ya existente no hace falta saber dónde está, y con un path anidado, mover una tarea cambiaría su propia URL.

**Mover es `PATCH /tasks/{taskId}` con `projectId` en el body.** No hay un endpoint `/move`. Es un cambio de un campo como cualquier otro. Y como el proyecto no está en ese path, mandarlo en el body no duplica nada. En el `POST` anidado sí lo duplicaría, por eso `TaskInput` no tiene `projectId`.

**`updatedAt` está en el contrato porque el front lo necesita.** El TP 1 no guarda el orden de las pilas: lo deriva de la prioridad y, entre las que empatan, de `updatedAt`. Ese campo llegó al contrato por un bug del TP 1 (ver su README). Un efecto que no busqué: como la pila se deriva, ninguna operación de esta API puede dejar una torre "ilegal". Si alguien sube la prioridad de una tarea enterrada, simplemente se reordena.

**404 es del path; 422 es del body.** `PATCH /tasks/17` con `{ "projectId": 99 }` responde 422, no 404. La tarea 17 existe; lo que está mal es un dato que mandó el cliente.

**409 al borrar un proyecto con tareas pendientes.** Borrar en cascada lo pendiente es perder trabajo sin aviso. Las tareas hechas sí se borran con el proyecto.

**`security: []` explícito.** Es un sistema de un solo usuario, sin autenticación. Prefiero que el contrato lo diga a que lo calle.

## Qué salió mal y cómo lo corregí

El prompt 1 salió bien a la primera, y ahí estaba el riesgo: un YAML válido que nadie contrastó contra el cliente que ya existe. El prompt 2 pidió exactamente eso, y aparecieron cuatro diferencias.

**En el YAML.** La respuesta compartida de 404 traía como ejemplo "El proyecto no existe." también en `/tasks/{taskId}`. Swagger le habría mostrado a quien lee que pedir una tarea inexistente devuelve un mensaje sobre proyectos. Quedó separada en `ProyectoNoExiste` y `TareaNoExiste`.

**En el TP 1, donde tiene razón el contrato.** Las anoto como deuda del final y no las corregí: el TP 1 ya está entregado.

1. `updateTask` con un `projectId` inexistente responde 404; el contrato dice 422.
2. `updateTask({})` responde 200 y cambia `updatedAt`. Como el front ordena por ese campo, un PATCH vacío podría reordenar una pila. El contrato lo rechaza con `minProperties: 1`.
3. Los campos desconocidos se ignoran en silencio. Por ejemplo, un `projectId` en el body del `POST` anidado. El contrato los rechaza con `additionalProperties: false`.

Ninguna de las tres se ve hoy, porque la interfaz del TP 1 nunca manda esos pedidos. Pero el final va a hacer que esos pedidos viajen por la red, y es ahí donde se van a ver.

**El linter.** `redocly lint` dio 10 errores, todos de `security-defined`, y se resolvieron con el `security: []` explícito. Agregué descripciones a los tags y la licencia. Quedaron dos advertencias que no corregí:

- `no-server-example.com`: el servidor es `localhost` porque todavía no hay un servidor desplegado.
- `operation-4xx-response` en `GET /projects`: listar todos los proyectos no tiene cómo fallar por culpa del cliente, e inventarle un 4xx sería mentir en el contrato.

## Cómo se ejecuta

Pegar [openapi.yaml](openapi.yaml) en [editor.swagger.io](https://editor.swagger.io). La documentación navegable aparece a la derecha.

Para validarlo:

```bash
npx @redocly/cli lint tp2/openapi.yaml
```

## Prompts

El registro completo está en [prompts.md](prompts.md). El primero fija el contrato. El segundo es el que importa: es la revisión cruzada contra el TP 1, de donde salen el arreglo del YAML y la deuda del final.
