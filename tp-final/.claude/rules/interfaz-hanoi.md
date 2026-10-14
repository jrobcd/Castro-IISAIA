---
paths:
  - "frontend/**"
  - "scripts/**"
---

# Interfaz

- Solo `js/api.js` usa `fetch`. Si otro archivo necesita datos, los pide a `app.js`, que llama a `api`.
- Las reglas van en `js/torres.js`, como funciones puras. `tablero.js` dibuja y no decide.
- La hostilidad es por reglas, no por esconder información: cada "no" tiene que decir por qué (qué tarea está arriba, cuántas hay encima).
- Las fechas se comparan con `Date.parse`, nunca como texto.
- Después de cualquier error de la API, se vuelve a leer todo (`ocupado()` ya lo hace). No dejar en pantalla un estado que el servidor no aceptó.
- Si cambia un id o una clase del DOM, actualizar `scripts/recorrido_navegador.py` y `frontend/CLAUDE.md`.
