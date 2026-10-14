# Trabajo Práctico Final — Tareas en torre, con servidor

La interfaz del TP 1, donde cada proyecto es una torre de Hanói y cada tarea un disco, ahora sobre un servidor que implementa el contrato del TP 2. El frontend es HTML, CSS y JavaScript sin paso de build. El backend es FastAPI con SQLite. Un solo proceso sirve las dos cosas.

Los dos TPs anteriores se pensaron para terminar acá. El TP 1 ya hablaba con un objeto `api` con forma de API REST, y el TP 2 especificó esa API. Este trabajo reemplaza el interior de ese objeto por `fetch` e implementa el contrato. La interfaz no cambió de comportamiento, y el contrato solo cambió en `servers` y en los ejemplos de `Location`.

## Cómo se ejecuta

Hace falta Python 3.11 o superior y [uv](https://docs.astral.sh/uv/). No hace falta internet, cuentas externas ni variables de entorno.

```bash
cd tp-final
uv sync
uv run fastapi dev backend/main.py
```

Abrir `http://127.0.0.1:8000`. El contrato navegable está en `http://127.0.0.1:8000/docs`, y ahí "Try it out" funciona contra el servidor real: en el TP 2 no había nada detrás.

La base `tareas.db` se crea al arrancar. Para empezar de cero alcanza con borrar ese archivo. Las tres torres (Trabajo, Facultad y Casa) las crea la interfaz la primera vez.

Si el puerto 8000 está ocupado:

```bash
uv run fastapi dev backend/main.py --port 8765
```

Tests de la API y del contrato. Usan una base temporal, así que no tocan `tareas.db`:

```bash
uv run pytest
```

Recorrido de la interfaz en un navegador. Se corre con el servidor levantado y la base vacía:

```bash
uv run --group e2e playwright install chromium     # una vez
uv run --group e2e python scripts/recorrido_navegador.py http://127.0.0.1:8000/
```

## Arquitectura

```
tp-final/
├── openapi.yaml        el contrato del TP 2, v1.1; /docs muestra este archivo
├── backend/
│   ├── main.py         app, tablas, contrato en /docs, montaje de estáticos
│   ├── db.py           engine de SQLite, foreign keys activadas, sesión por request
│   ├── models.py       tablas Project y Task
│   ├── schemas.py      lo que entra y lo que sale, separado de las tablas
│   ├── errores.py      todo error sale como { status, message }, en castellano
│   └── routes.py       las 10 operaciones; cada función se llama como su operationId
├── frontend/
│   ├── index.html
│   ├── css/estilos.css
│   └── js/
│       ├── api.js      fetch; mismos métodos que el `api` del TP 1
│       ├── torres.js   reglas de Hanói, funciones puras
│       ├── tablero.js  dibuja las torres
│       └── app.js      estado y eventos
├── tests/
│   ├── contrato.py     valida una respuesta contra openapi.yaml
│   ├── conftest.py     base temporal y un cliente que valida toda respuesta
│   ├── test_proyectos.py
│   ├── test_tareas.py  incluye las tres deudas del TP 2
│   └── test_contrato.py  ninguna operación de más ni de menos
├── scripts/
│   └── recorrido_navegador.py
└── docs/
    └── plan.md         el plan con el que arranqué, sin editar
```

### Endpoints

Son los diez del contrato, bajo `/api`. El detalle está en [openapi.yaml](openapi.yaml) o en `/docs`.

| Método | Path | Respuestas |
|--------|------|------------|
| `GET` | `/api/projects` | `200` |
| `POST` | `/api/projects` | `201` + `Location` · `422` |
| `GET` | `/api/projects/{projectId}` | `200` · `404` |
| `PATCH` | `/api/projects/{projectId}` | `200` · `404` · `422` |
| `DELETE` | `/api/projects/{projectId}` | `204` · `404` · `409` si tiene tareas pendientes |
| `GET` | `/api/projects/{projectId}/tasks?done=` | `200` · `404` (no una lista vacía) |
| `POST` | `/api/projects/{projectId}/tasks` | `201` + `Location` · `404` · `422` |
| `GET` | `/api/tasks/{taskId}` | `200` · `404` |
| `PATCH` | `/api/tasks/{taskId}` | `200` · `404` · `422` (incluye un proyecto destino inexistente) |
| `DELETE` | `/api/tasks/{taskId}` | `204` · `404` |

### Datos

Hay dos tablas:

- `Project`: `id`, `name`, `created_at` y `updated_at`.
- `Task`: `id`, `project_id` (foreign key), `title`, `priority` (de 1 a 5), `done`, `created_at` y `updated_at`.

La API las expone en camelCase, como dice el contrato. Ninguna tabla guarda la posición de una tarea en su torre: el orden se deriva.

### Contrato entre la interfaz y el servidor

```
PATCH /api/tasks/7
{ "projectId": 3 }

200
{ "id": 7, "projectId": 3, "title": "Leer el paper", "priority": 3, "done": false,
  "createdAt": "2026-10-14T22:10:03.118204Z", "updatedAt": "2026-10-14T22:31:47.902311Z" }
```

Mover una tarea es eso: un PATCH de un campo. El servidor no sabe de torres.

## Qué decidí yo

**Implementar el contrato del TP 2, no escribir uno nuevo.** FastAPI genera su propio OpenAPI a partir del código. Lo descarté como fuente de verdad: en ese caso, el contrato documenta lo que el código hizo, y yo quería lo contrario. `/docs` sirve `openapi.yaml` tal cual. Para que el YAML no quede como texto decorativo, el cliente de los tests valida **cada respuesta** contra él: status documentado, body que cumple el schema y `Location` cuando corresponde. Un test aparte comprueba que cada operación del YAML exista con su `operationId` como nombre de función, y que no haya rutas de más.

**El contrato se copió y se versionó.** El TP 2 está entregado y no se toca. La copia de acá es la v1.1, y solo cambian `servers` (de `localhost:3000` a `/api`) y los ejemplos de `Location`. Ningún schema ni status code cambió, y eso es lo que más me interesa mostrar del TP 2: el contrato aguantó una implementación real.

**Las reglas de Hanói siguen solo en la interfaz.** El servidor deja mover cualquier tarea a cualquier proyecto. Como la pila se deriva de la prioridad y de `updatedAt`, ninguna operación de la API puede dejar una torre ilegal. A lo sumo la reordena.

**Sin login.** El ejemplo de la cátedra usa Auth0. Acá no lo puse, por tres razones: el contrato del TP 2 declara `security: []` a propósito; la consigna pide que corra local; y no quería que levantar el TP dependiera de una cuenta externa. Es un sistema de un solo usuario. Si hubiera usuarios, el primer cambio sería el contrato, no el código.

**Modo estricto en la entrada.** Pydantic, por defecto, convierte `"3"` en `3` y `"true"` en `True`. El contrato dice `integer` y `boolean`, así que la entrada es `strict=True` y `extra="forbid"`. Un null explícito en un PATCH también es 422: el contrato no declara campos nullable.

**404 es del path, 422 es del body, también para FastAPI.** Si el id del path no es un entero, FastAPI responde 422 por defecto. Acá responde 404: un recurso cuyo id ni siquiera es entero no existe, y "el path no existe" es justamente lo que significa 404 en el contrato.

**Un solo archivo habla con el servidor.** `api.js` tiene los mismos métodos y firmas que el `api` del TP 1, y rechaza con la misma forma (`{ status, message }`). `app.js` es casi el script del TP 1, partido para respetar el límite de tamaño. La diferencia es que antes los errores eran de validación y ahora también pueden ser de red (`status: 0`).

**La siembra de las tres torres la hace la interfaz.** "Tres proyectos" es una regla de la Bad UI. Si el servidor sembrara tres, sabría algo que no le corresponde.

**El contador de movimientos queda en el navegador.** Es un dato de esta interfaz, no del sistema.

## Cómo gestioné el contexto

Trabajé en modo plan antes de escribir código. El agente leyó `tp1/`, `tp2/` y la estructura del ejemplo de la cátedra, y me hizo cuatro preguntas: qué se reutiliza del TP 1, qué se reutiliza del TP 2, si hacía falta login y qué stack usar. Con las respuestas escribió [docs/plan.md](docs/plan.md), que quedó sin editar.

El contrato funcionó como el contexto más barato del proyecto. Para trabajar en el backend, el agente no necesitaba leer el frontend, y al revés tampoco: `openapi.yaml` describe en unas 300 líneas todo lo que cruza la frontera. Es lo que se dijo en clase sobre los YAML de OpenAPI, y acá se notó. Por eso el YAML es lo primero que se toca en la skill `cambiar-contrato`.

Trabajé por piezas, y cada una terminó en verde antes de pasar a la siguiente:

1. backend con sus tests;
2. validación contra el contrato;
3. frontend con el recorrido en Chromium;
4. configuración del agente e informe.

Los archivos están por debajo de 300 líneas. El más largo es `app.js`, con 156. Separar `tablero.js` de `app.js` permite tocar el dibujo sin cargar la lógica, y separar `torres.js` deja las reglas en un archivo que no depende ni del DOM ni de la red.

La configuración del agente está versionada junto al código:

- **`CLAUDE.md`:** uno general y uno en `backend/` y otro en `frontend/`, que se cargan solo al trabajar ahí.
- **Dos reglas en `.claude/rules/`:** se aplican por ruta.
- **`.claude/settings.json`:**
  - el agente puede editar `backend/`, `frontend/`, `tests/` y `scripts/` sin preguntar;
  - pregunta antes de tocar `openapi.yaml` y el README;
  - tiene prohibido tocar `docs/plan.md`, `tp1/` y `tp2/`.
- **La skill `cambiar-contrato`:** el procedimiento completo para cambiar la API, con el YAML primero y el README al final.
- **Un sub-agente explorador de solo lectura:** para preguntas que cruzan las dos mitades.
- **Los comandos `/explicar` y `/pre-entrega`.**

La verificación tuvo tres niveles:

1. `pytest` sobre la API, con cada respuesta validada contra el contrato.
2. Antes de confiar en ese validador, lo probé con siete respuestas rotas a propósito: status no documentado, falta `Location`, `done` como string, falta `updatedAt`, error con la forma `{ detail }` de FastAPI, 204 con cuerpo y una lista con un elemento roto. Detectó las siete.
3. Un recorrido en Chromium con Playwright, que repite los bugs del TP 1 y suma dos casos nuevos: dos pestañas y el servidor caído.

El plan y lo construido no coinciden del todo:

- **Archivos que el plan no tenía:**
  - `tablero.js`, que salió de partir `app.js`;
  - `errores.py`, que salió de que el handler de errores no entraba prolijo en `main.py`;
  - `scripts/recorrido_navegador.py`, porque el plan decía "se verifica en el navegador" sin decir cómo repetirlo.
- **La validación del contrato:** el plan la ponía en un `test_contrato.py` con sus propios casos. Terminó en el cliente de todos los tests, que cubre más con menos código. `test_contrato.py` quedó solo para comparar las operaciones del YAML con las rutas.
- **El contrato:** el plan decía "copia del TP 2". En el camino se vio que la copia necesitaba los cambios de `servers` y `Location`.

## Qué salió mal

**Borrar un proyecto violaba la foreign key.** Un proyecto con solo tareas hechas tiene que borrarse junto con ellas. El test falló con `FOREIGN KEY constraint failed`. Los modelos no declaran `relationship`, así que el unit of work de SQLAlchemy no sabe que las tareas van antes, y mandó primero el `DELETE` del proyecto. Lo encontré solo porque `db.py` activa `PRAGMA foreign_keys`. SQLite, por defecto, no las controla, y sin eso el test habría pasado dejando tareas huérfanas en la base. La corrección es borrar las tareas con una sentencia propia antes del proyecto. No agregué una cascada: el 409 con tareas pendientes es una decisión del contrato, y una cascada lo volvería fácil de romper.

**Un test que pasaba sin probar nada.** `test_contrato.py` tiene dos direcciones: toda operación del YAML existe en el código, y ninguna ruta del código falta en el YAML. La primera falló: decía que no existía ni `GET /projects`. En FastAPI 0.143, un router incluido queda envuelto en un objeto privado, y sus rutas no aparecen en `app.routes`. Lo grave era la segunda dirección: compara el conjunto de rutas con el de operaciones, y un conjunto vacío está incluido en cualquier otro, así que **pasaba**. Si hubiera escrito solo esa, el test estaría en verde sin mirar nada. Ahora recorre `router.routes`, que es API pública. Desde ahí, ante un test de cobertura en verde, me pregunto también sobre qué conjunto está iterando.

**El contrato del TP 2 no servía tal cual para un servidor real.** Tenía `servers: http://localhost:3000`, y los ejemplos de `Location` eran `/projects/2`. Con la API bajo `/api`, un cliente que siguiera ese `Location` lo resolvería contra la raíz del sitio y terminaría en un archivo estático. No era un error del TP 2, porque ahí no había servidor: era un supuesto que nadie había puesto a prueba. Cambiaron esos dos datos y la versión menor, y nada más.

**Las fechas no se pueden comparar como texto.** El TP 1 desempataba las pilas con `localeCompare` sobre `updatedAt`, y ahí andaba porque `toISOString()` siempre escribe los milisegundos. Pydantic, en cambio, omite la parte fraccionaria cuando vale cero: `12:00:00Z` y `12:00:00.500000Z`. Como texto, la segunda queda antes, porque `.` va antes que `Z`. Pasa una vez cada millón de escrituras, nunca en una demo y siempre en algún momento. Lo vi al portar el desempate y lo confirmé serializando las dos fechas. `torres.js` ahora usa `Date.parse`. Después encontré la misma trampa en mis propios tests, que comparaban `updatedAt` como texto. Ahora comparan con `datetime.fromisoformat`.

**El disco que se teletransportaba.** Con un servidor, aparece un caso que en el TP 1 no existía: dos pestañas. En el recorrido, una pestaña levantaba una tarea y la otra la mudaba de torre. Al volver a la primera, la tarea seguía levantada, pero en otra torre. La regla del TP 1 ("se suelta si ya no está arriba") no lo detectaba, porque la tarea estaba arriba, solo que de otra torre. Ahora la interfaz recuerda de qué torre se levantó, y la suelta si cambió. Lo encontró el recorrido en el navegador, no los tests de la API: es una regla de la interfaz, y el servidor hizo exactamente lo que el contrato dice.

**Las tres deudas del TP 2 se pagaron sin tocar la interfaz.** El TP 2 dejó anotado que el `api` del TP 1 respondía 404 donde el contrato dice 422, aceptaba un PATCH vacío e ignoraba campos desconocidos. Las tres estaban en la capa que este trabajo reemplazó, así que se resolvieron implementando el contrato, y cada una tiene su test (`test_deuda_1…3`). La interfaz no se enteró: nunca mandaba esos pedidos.

## Prompts

El registro completo está en [prompts.md](prompts.md).
