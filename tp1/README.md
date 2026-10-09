# TP 1 — Tareas en torre

Un gestor de tareas donde cada proyecto es una torre de Hanói y cada tarea es un disco. Cuanto más prioritaria es la tarea, más ancho es el disco, así que lo urgente termina abajo de todo. Funciona: se crean, se mueven, se completan y se borran tareas. Usarlo es una condena, que era la idea.

## Qué construí

Una Bad UI hostil por reglas y no por capricho. No esconde nada: las reglas están escritas en el encabezado y cada torre muestra cuántos movimientos cuesta mudarla. Aun así duele, porque solo se toca la tarea de arriba y nunca va una más prioritaria sobre una menos prioritaria. Para llegar a lo importante hay que desarmar la pila.

Este TP es además la primera capa de un sistema de tres partes. El TP 2 es el contrato REST de proyectos y tareas, y el final conecta las dos. Por eso la hostilidad vive solo en la interfaz, y los datos se manejan como si ya hubiera una API detrás.

## Cómo lo dirigí

Tres prompts en una sola sesión de Claude Code. El primero fija el modelo de datos con los nombres del futuro contrato, las siete reglas de la interfaz y la separación entre datos e interfaz. El segundo junta los cuatro defectos que encontré al probar. El tercero hace visible el costo. Después de cada respuesta probé simulando clics sobre el DOM, sin limitarme a leer el código.

## Decisiones que tomé yo

**Un objeto `api` con forma de API REST, aunque por ahora guarde en `localStorage`.** Es la decisión que conecta los tres TPs. Cada método devuelve una `Promise`, tarda unos milisegundos y falla con `{ status, message }`: 404 si no existe, 409 si hay conflicto, 422 si el dato es inválido. La interfaz ya está escrita contra eso. En el final solo cambia el interior de `api` por `fetch`.

**Las reglas de Hanói no están en `api`.** La api deja mover cualquier tarea a cualquier proyecto. La que dice "no entra" es la interfaz. Si la regla estuviera en los datos, el TP 2 tendría que especificar un endpoint de "mover respetando Hanói", y eso es una broma de UI metida en un contrato.

**La pila no se guarda: se deriva.** El orden de una torre sale de ordenar por prioridad y, entre las que empatan, por `updatedAt`. No hay un campo `position`. Funciona porque solo se puede modificar la tarea de arriba, así que `updatedAt` nunca reordena algo enterrado. Ver "Qué salió mal".

**Tres proyectos, ni uno más.** Con cuatro torres, Hanói se vuelve mucho más fácil. La api acepta N proyectos; la interfaz muestra tres. Es otra restricción de la interfaz que no pasa al contrato.

**Igual prioridad se puede apilar.** Con prioridades estrictas, cinco niveles alcanzarían para cinco tareas por torre. Permitir empates hace que entre cualquier cantidad, y el estado nunca queda sin salida: con tres torres, cualquier configuración válida llega a cualquier otra.

**Lo urgente, abajo.** Es la inversión de fondo de esta Bad UI. Un gestor de tareas existe para que lo importante esté a mano, y acá está enterrado.

## Qué salió mal y cómo lo corregí

Moví una tarea de prioridad 3 sobre otra de prioridad 3 y apareció **debajo**. El movimiento siguiente se llevó a la otra.

El problema estaba en mi prompt, no en el código. Definí `Task { id, projectId, title, priority, done, createdAt }` y pedí una pila, pero el orden de la pila es estado, y mi modelo no tenía con qué representarlo. La implementación hizo lo razonable con lo que tenía: desempatar por `createdAt`. Pero `createdAt` dice cuándo nació la tarea, no cuándo llegó a esa torre.

La salida fácil era agregar `position`. No la tomé porque obligaba a la API del TP 2 a saber de pilas. Pedí desempatar con un dato que una API REST tendría de todos modos, y quedó `updatedAt`, generado por el servidor. Este error le cambia el modelo al TP 2: `updatedAt` tiene que estar en el contrato porque el front lo necesita para dibujar.

Con el mismo prompt arreglé otros tres defectos que encontré al probar:

- **Una tarea levantada quedaba levantada aunque le apilaran otra encima con el formulario.** Se podía mover desde abajo. Ahora, cada vez que se recargan los datos, la selección se suelta si esa tarea ya no está arriba.
- **Un doble clic en Borrar mandaba dos pedidos.** El segundo terminaba en 404. Ahora hay una sola operación a la vez.
- **Si la api rechazaba un nombre vacío, el campo quedaba vacío.** Ahora, ante cualquier error, la interfaz vuelve a leer todo: nunca muestra un estado que la api no aceptó.

Este último es el patrón que va a necesitar el final, cuando los errores vengan de la red.

Lo que sí funcionó por diseño fue pedir que la fórmula del costo se verificara antes de mostrarla. 2ⁿ − 1 solo vale con prioridades distintas. Con empates el mínimo es otro (C(k) = 2·C(k−1) + m_k, por grupos), y lo contrasté con el óptimo calculado por BFS en las 461 torres posibles de hasta seis tareas.

## Cómo se ejecuta

Doble clic en `index.html`. Es un solo archivo, sin dependencias ni servidor. Los datos quedan en el `localStorage` del navegador; para empezar de cero, hay que borrar los datos del sitio.

## Prompts

El registro completo está en [prompts.md](prompts.md). El que más pesó fue el primero, porque fija el modelo y la frontera entre `api` e interfaz. El segundo es el que le cambió el modelo al TP 2.
