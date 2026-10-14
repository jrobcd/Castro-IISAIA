# Plan — Tareas en torre, versión con servidor

Plan escrito en modo plan antes de tocar código, a partir de `tp1/` y `tp2/` y de las respuestas a cuatro preguntas. No se actualiza: las diferencias con lo construido se explican en el README.

## Respuestas que fijan el plan

1. **¿Qué se reutiliza del TP 1?** La interfaz y las reglas de Hanói, sin cambios de comportamiento. Se reemplaza el objeto `api`: deja de usar `localStorage` y pasa a usar `fetch`.
2. **¿Qué se reutiliza del TP 2?** El contrato, que es la fuente de verdad. La implementación tiene que cumplirlo y los tests lo comprueban contra el YAML, no contra una copia escrita a mano.
3. **¿Login?** No. El contrato declara `security: []` y la consigna pide que corra local. Un solo usuario.
4. **¿Stack?** FastAPI + SQLite en un solo proceso, que sirve la API y los estáticos. Frontend sin build: ES modules nativos.

## Estructura

```
tp-final/
├── pyproject.toml
├── openapi.yaml          copia del contrato del TP 2
├── backend/
│   ├── main.py           app, handlers de error, tablas, montaje de estáticos
│   ├── db.py             engine y sesión por request
│   ├── models.py         Project, Task
│   ├── schemas.py        entrada y salida, separadas de las tablas
│   └── routes.py         las 10 operaciones
├── frontend/
│   ├── index.html
│   ├── css/estilos.css
│   └── js/
│       ├── api.js        mismo nombre y firma de métodos que el `api` del TP 1, con fetch
│       ├── torres.js     reglas puras: pila, cima, entra, costoMudanza
│       └── app.js        dibujo y eventos
└── tests/
    ├── conftest.py       base temporal
    ├── test_proyectos.py
    ├── test_tareas.py
    └── test_contrato.py  cada respuesta se valida contra openapi.yaml
```

## Endpoints

Los del contrato, bajo el prefijo `/api`:

| Método | Path | Éxito | Errores |
|--------|------|-------|---------|
| GET | /projects | 200 | — |
| POST | /projects | 201 + Location | 422 |
| GET | /projects/{projectId} | 200 | 404 |
| PATCH | /projects/{projectId} | 200 | 404, 422 |
| DELETE | /projects/{projectId} | 204 | 404, 409 |
| GET | /projects/{projectId}/tasks?done= | 200 | 404 |
| POST | /projects/{projectId}/tasks | 201 + Location | 404, 422 |
| GET | /tasks/{taskId} | 200 | 404 |
| PATCH | /tasks/{taskId} | 200 | 404, 422 |
| DELETE | /tasks/{taskId} | 204 | 404 |

Todos los errores tienen la forma `{ status, message }`, con el mensaje en castellano.

## Orden de trabajo

Una pieza por vez. Cada pieza termina con algo que se puede correr.

1. **Backend + tests de la API.** `uv run pytest` en verde, incluidas las tres deudas del TP 2.
2. **Test de contrato.** Las respuestas del paso 1 se validan contra `openapi.yaml`.
3. **Frontend.** El `index.html` del TP 1 partido en módulos, con `api.js` usando fetch. Se verifica en el navegador.
4. **README e informe.**

## Riesgos que veo

- El 422 de FastAPI tiene otra forma (`{ detail: [...] }`). Hace falta un handler que lo traduzca a `{ status, message }`.
- El TP 1 desempata las pilas por `updatedAt`, así que el servidor tiene que actualizarlo en cada PATCH, incluida la mudanza.
- La siembra de las tres torres hoy la hace la interfaz. Se queda ahí: el servidor no sabe que la interfaz muestra tres.
