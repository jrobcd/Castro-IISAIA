# frontend/

## Por qué no hay build

Son ES modules nativos, sin dependencias. Como los módulos no cargan desde `file://`, la página se abre siempre a través del servidor (`http://127.0.0.1:8000`). El TP 1 se abría con doble clic porque era un solo archivo con el script en línea.

## Quién llama a quién

```
index.html ─▶ js/app.js ─▶ js/api.js      (fetch; único que habla con el servidor)
                      ├──▶ js/torres.js   (reglas puras: pila, cima, entra, costoMudanza)
                      └──▶ js/tablero.js  (dibuja; recibe el estado y los manejadores)
                                └──▶ js/torres.js
```

- **`app.js`** tiene el estado (`proyectos`, `tareas`, `elegida`, `elegidaEn`, `movimientos`) y decide. Toda operación pasa por `ocupado()`, que permite una sola a la vez y vuelve a leer todo si la API rechaza algo.
- **`tablero.js`** no decide nada. Cada clic lo deriva a `manejadores` (`disco`, `torre`, `renombrar`, `borrarHecha`).
- **`torres.js`** no toca ni el DOM ni la API, así que se puede razonar (y probar) aparte.

## Ids del DOM

`#form-nueva`, `#nueva-titulo`, `#nueva-prioridad`, `#nueva-proyecto`, `#mensaje`, `#movimientos`, `#acciones`, `#btn-completar`, `#btn-borrar`, `#btn-soltar` y `#tablero`. Las torres son `.torre`, los discos `.disco`, el disco levantado `.disco.elegido` y el botón de destino `button.aca`. `scripts/recorrido_navegador.py` depende de estos selectores.

## Errores

`api.js` rechaza con `{ status, message }`. `status: 0` significa que no hay conexión. El resto del frontend solo muestra `err.message`.

## Qué es de la interfaz y qué es del servidor

| De la interfaz | Del servidor |
|----------------|--------------|
| tres torres, "no entra", "solo la de arriba" | que la tarea exista, que el proyecto destino exista |
| contador de movimientos (`localStorage`) | `updatedAt` |
| sembrar Trabajo, Facultad y Casa | nada sobre cuántos proyectos hay |
