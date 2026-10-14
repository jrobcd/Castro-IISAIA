# Registro de prompts — Trabajo Práctico Final

Herramienta: Claude Code, en una sola sesión, con el repositorio abierto (`tp1/`, `tp2/` y `tp-final/`). Los prompts van tal como se enviaron. Debajo de cada uno, en cursiva, anoto qué hice con la respuesta.

---

## Prompt 1 — modo plan

```
Modo plan, sin escribir código todavía.

Contexto: TP final. Consigna: una aplicación local, no trivial, que muestre
evolución durante el curso; primera versión funcional para presentar en 6
minutos. La cátedra mostró como referencia un proyecto FastAPI + SQLite que
sirve un frontend sin build desde el mismo proceso, con CLAUDE.md por carpeta,
reglas, skill, sub-agente y un README que es informe (qué decidí, cómo gestioné
el contexto, qué salió mal).

Mi idea: que el final sea la integración de mis dos TPs. tp1/index.html es una
Bad UI de tareas sobre torres de Hanói que ya habla con un objeto `api` con
forma REST (hoy en localStorage). tp2/openapi.yaml es el contrato de esa API.
El final implementa el contrato y le cambia el interior a `api`.

Leé tp1/ y tp2/ completos, incluidos los README, que tienen decisiones y
deudas anotadas. Antes de escribir el plan, haceme las preguntas cuyas
respuestas cambien el plan. No más de cuatro.
```

*El agente hizo cuatro preguntas: qué se reutiliza del TP 1, qué se reutiliza del TP 2, si hace falta login y qué stack usar.*

---

## Prompt 2 — respuestas

```
1. Del TP 1: la interfaz y las reglas, sin cambiar comportamiento. Solo cambia
   el interior de `api`.
2. Del TP 2: el contrato es la fuente de verdad. No quiero que /docs muestre
   un OpenAPI generado desde el código; quiero que los tests validen las
   respuestas reales contra el YAML.
3. Login: no. El contrato dice security: [] y la consigna pide local. Si
   pensás que eso hace el proyecto "demasiado simple", decímelo con
   argumentos, no lo agregues.
4. Stack: el de la cátedra. FastAPI + SQLite, un proceso, frontend sin build.

Escribí el plan en tp-final/docs/plan.md. Ese archivo queda congelado: lo que
cambie después se explica en el README, no se edita el plan. Incluí el orden
de trabajo por piezas, cada una terminando en algo que se pueda correr, y los
riesgos que veas.
```

*Plan escrito. Señaló tres riesgos: la forma del 422 de FastAPI, que `updatedAt` cambie en cada PATCH y quién siembra las tres torres. Sobre el login, argumentó que lo no trivial está en el contrato verificado, y lo acepté.*

---

## Prompt 3 — pieza 1: backend

```
Pieza 1 del plan: backend con sus tests.

- Capas como en el ejemplo de la cátedra: db, models, schemas, routes, main.
- Las funciones de routes.py se llaman como los operationId.
- Errores siempre { status, message } en castellano, nunca { detail }.
- Entrada estricta: "3" no es un entero. Campos desconocidos y PATCH vacío
  son 422.
- Las tres deudas del TP 2 van como tests con nombre propio.
- Tests con base temporal; no pueden tocar tareas.db.

Terminá cuando uv run pytest esté en verde. Si un test falla, quiero saber
la causa antes del arreglo.
```

*Un test falló: borrar un proyecto con solo tareas hechas violaba la foreign key. La causa era el orden de borrado del unit of work, sin `relationship` declarada. Se corrigió borrando primero las tareas, con una sentencia propia. 24 tests en verde.*

---

## Prompt 4 — pieza 2: contrato

```
Pieza 2: que el contrato no sea decorativo.

- Toda respuesta de /api que pase por el cliente de los tests se valida
  contra openapi.yaml: status documentado para esa operación, body contra el
  schema, headers documentados presentes, 204 sin cuerpo.
- Un test que compare operaciones del YAML con rutas del código en las dos
  direcciones.
- /docs sirve el YAML tal cual.

Antes de darme el validador por bueno, demostrame que falla: armá respuestas
rotas a mano y mostrame que detecta cada una.
```

*El test de cobertura no encontraba ninguna ruta: en FastAPI 0.143, `app.routes` no lista las de un router incluido. La dirección "ninguna ruta de más" pasaba igual, porque comparaba un conjunto vacío. Se corrigió recorriendo `router.routes`. El validador detectó las 7 respuestas rotas. También hubo que adaptar `servers` y `Location` en la copia del contrato.*

---

## Prompt 5 — pieza 3: frontend

```
Pieza 3: el frontend.

Partí tp1/index.html en index.html + css + módulos ES. Separación:
- api.js: único archivo con fetch. Mismos métodos y firmas que el `api` del
  TP 1, mismo formato de rechazo. Sin conexión → status 0 y mensaje en
  castellano.
- torres.js: las reglas como funciones puras.
- el dibujo separado del estado y los eventos.
Cero cambios de comportamiento respecto del TP 1.

Verificalo en un navegador real (Playwright + Chromium), no con jsdom. Casos:
los cuatro bugs que rompieron el TP 1, más los que antes no podían existir:
dos pestañas sobre los mismos datos, y el servidor caído con la página
abierta. Dejá el recorrido como script en el repo, con asserts.
```

*Pasaron los casos del TP 1 y el del servidor caído. Falló el de dos pestañas: una tarea levantada en una pestaña seguía levantada después de que la otra la mudara de torre. Ver el prompt 6.*

---

## Prompt 6 — decisión sobre las pestañas

```
Lo de las dos pestañas no es un bug del servidor, es una regla de la
interfaz que el TP 1 nunca tuvo que definir. Decisión: una tarea levantada
se suelta si al recargar ya no está arriba de la torre de la que salió,
aunque esté arriba de otra. Agregalo como caso al recorrido.

Además, revisá el desempate de las pilas: ahora updatedAt lo genera Python,
no toISOString(). ¿Sigue siendo válido compararlo como texto?
```

*No era válido. Pydantic omite los microsegundos cuando valen cero, y como texto `…:00Z` queda después de `…:00.5Z`. Lo confirmé serializando las dos fechas. `torres.js` pasó a `Date.parse`, y los tests, que tenían la misma comparación, a `datetime.fromisoformat`.*

---

## Prompt 7 — configuración del agente

```
Pieza 4a: la configuración del agente, versionada con el código, siguiendo la
estructura del ejemplo de la cátedra pero con contenido de este proyecto:

- CLAUDE.md raíz (panorama, comandos, los contratos de diseño, trampas ya
  pagadas, convenciones) y uno en backend/ y otro en frontend/.
- Dos reglas en .claude/rules/ con paths: una para API/contrato, una para la
  interfaz.
- settings.json: editar backend, frontend, tests y scripts sin preguntar;
  preguntar antes de tocar openapi.yaml y el README; prohibido docs/plan.md,
  tp1/ y tp2/.
- Una skill con el procedimiento para cambiar la API, empezando por el YAML.
- Un sub-agente explorador de solo lectura.
- /explicar <archivo> y /pre-entrega.

Las "trampas ya pagadas" tienen que ser las que pagamos en esta sesión, no
consejos genéricos.
```

*Hecho.*

---

## Prompt 8 — informe

```
Pieza 4b: el README como informe, con las secciones del ejemplo de la
cátedra. "Qué salió mal" cuenta solo lo que pasó en esta sesión, con causa y
corrección. Las diferencias entre docs/plan.md y lo construido van en
"Cómo gestioné el contexto". Antes de entregármelo, verificá cada afirmación
que no hayas comprobado todavía (cantidades de líneas, que "Try it out"
funcione en /docs).
```

*Verificado: `openapi.yaml` tiene 314 líneas, `app.js` tiene 156, y "Try it out" en `/docs` llama a `/api/projects` y responde 200 con datos reales.*
