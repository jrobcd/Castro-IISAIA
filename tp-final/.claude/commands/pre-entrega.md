---
description: Revisa que el TP final esté en condiciones de entregarse.
---

Revisá, en este orden, y reportá cada punto como OK o FALLA con la evidencia:

1. `uv run pytest`: todo en verde.
2. `npx @redocly/cli lint openapi.yaml`: válido, sin advertencias nuevas además de las justificadas en el README.
3. Ningún archivo de `backend/`, `frontend/`, `tests/` ni `scripts/` supera las 300 líneas.
4. Toda operación de `openapi.yaml` tiene su método en `frontend/js/api.js` o una razón en el README para no tenerlo.
5. `README.md` no menciona archivos, comandos ni comportamientos que ya no existen. Contrastalo contra el árbol real.
6. `docs/plan.md`, `../tp1/` y `../tp2/` no tienen cambios respecto del último commit (`git diff --stat`).
7. `prompts.md` termina con el último prompt usado.

No arregles nada: solo reportá.
