# Registro de prompts — TP 1

Herramienta: Claude Code, en una sola sesión, con el repositorio abierto. Los prompts van tal como se enviaron. Debajo de cada uno, en cursiva, anoto qué hice con la respuesta.

---

## Prompt 1

```
Contexto: TP 1 de "Introducción a la ingeniería de software asistida por IA".
Consigna: una aplicación funcional con interfaz mala (incómoda pero operativa),
en un único archivo HTML con CSS y JS embebidos. Este TP es además la capa de
presentación de un sistema que en el TP 2 voy a especificar como API REST de
proyectos y tareas, y que en el final voy a integrar. Lo que decidas acá tiene
que sobrevivir a ese reemplazo.

Objetivo: un gestor de tareas en tp1/index.html donde cada proyecto es una
torre de Hanói y cada tarea es un disco.

Modelo de datos (no cambies los nombres, son los del futuro contrato):
- Project { id, name, createdAt }
- Task    { id, projectId, title, priority (entero 1–5), done (boolean), createdAt }

Reglas de la interfaz:
1. Exactamente tres proyectos, tres torres.
2. El ancho del disco es proporcional a priority; 5 es el más ancho.
3. Solo se interactúa con la tarea de arriba de cada torre: mover, completar, borrar.
4. Mover = clic en la tarea de arriba, clic en la torre destino. No se puede
   poner una tarea sobre otra de menor prioridad; sobre una de igual prioridad sí.
5. Crear una tarea la apila arriba de la torre elegida, con la misma regla.
6. Completar saca la tarea de la torre (done = true) y la lista debajo.
7. Contador de movimientos.

Arquitectura:
- Toda lectura y escritura pasa por un objeto `api` cuyos métodos devuelven
  Promise y fallan con { status, message } (404, 409, 422), como un fetch.
  Persistencia en localStorage, con una latencia artificial chica para que la
  UI no asuma respuestas sincrónicas.
- Las reglas de Hanói viven en la UI, no en `api`: la api acepta cualquier
  cambio que sea válido como dato.
- DOM, no canvas. Sin dependencias externas.

Criterios de aceptación: se abre con doble clic; recargar conserva el estado;
la UI nunca queda en un estado sin salida.
```

*Lo probé simulando clics sobre el DOM (jsdom). Lo básico anduvo, pero encontré cuatro defectos y con ellos armé el prompt 2.*

---

## Prompt 2

```
Probé la versión 1 con clics reales. Encontré cuatro defectos. Para cada uno
quiero la causa, no solo el parche.

1. Muevo "A" (prioridad 3) sobre "B" (prioridad 3): A aparece DEBAJO de B, y
   el siguiente movimiento de esa torre se lleva a B. La tarea que acabo de
   apilar se hunde.
2. Levanto la tarea de arriba de una torre, después uso el formulario para
   apilar otra encima de esa misma torre, y la que tenía levantada todavía se
   puede mover desde abajo. Rompe la regla 3.
3. Doble clic en "Borrar": el segundo pedido llega con la tarea ya borrada y
   aparece "La tarea no existe".
4. Renombro un proyecto con nombre vacío: la api devuelve 422, pero el campo
   queda vacío en pantalla.

Restricciones para el arreglo del 1: no quiero un campo de posición en el
modelo. El orden de la pila es estado de la interfaz y la API del TP 2 no
tiene por qué saber de pilas. Si hace falta un dato para desempatar, que sea
uno que una API REST tendría de todos modos.

Además: hoy la torre destino solo se elige con el mouse. Agregá una forma de
elegirla con el teclado.
```

*Del 1 salió la decisión más importante del TP; la cuento en el README. El arreglo agregó `updatedAt` al modelo. Volví a correr los cuatro casos y además verifiqué la persistencia y el teclado.*

---

## Prompt 3

```
Ahora quiero que la incomodidad se pueda leer. La interfaz no tiene que
esconder por qué duele.

- Debajo de cada torre, mostrá el mínimo de movimientos para mudarla entera a
  otra torre, con la tercera libre. Ojo: las prioridades se repiten, así que
  2^n − 1 solo vale cuando todas son distintas. Derivá la fórmula para
  prioridades repetidas y, antes de mostrarla, contrastala con el óptimo
  calculado por BFS en todas las torres de hasta 6 tareas.
- Si toco una tarea enterrada, el mensaje tiene que decir cuántas tareas
  tiene encima.
- En el encabezado, una línea que diga que lo urgente queda abajo y cuánto
  cuesta mudar una torre.
```

*La fórmula es C(k) = 2·C(k−1) + m_k, por grupos de igual prioridad contando desde arriba. Coincidió con el BFS en las 461 torres posibles de hasta 6 tareas.*
