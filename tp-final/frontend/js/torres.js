// Las reglas de Hanói. Funciones puras: reciben tareas, no tocan el DOM ni la API.
// El servidor no conoce nada de esto.

// Cuándo llegó la tarea a su torre. Se compara como fecha y no como texto: el
// servidor omite los microsegundos cuando valen cero, y "…:00Z" > "…:00.5Z" como string.
const llegada = t => Date.parse(t.updatedAt || t.createdAt);

// La pila no se guarda: se deriva. Abajo la más prioritaria; a igual prioridad, la
// que llegó antes. Como solo se modifica la de arriba, updatedAt no reordena lo enterrado.
export function pila(tareas) {
  return tareas
    .filter(t => !t.done)
    .sort((a, b) => b.priority - a.priority || llegada(a) - llegada(b) || a.id - b.id);
}

export function cima(tareas) {
  const p = pila(tareas);
  return p[p.length - 1] || null;
}

export function entra(tarea, tareasDestino) {
  const arriba = cima(tareasDestino);
  return !arriba || tarea.priority <= arriba.priority;
}

// Mínimo de movimientos para mudar una torre entera, con la tercera libre.
// Con prioridades distintas es 2^n − 1; con repetidas se cuenta por grupos desde
// arriba: C(k) = 2·C(k−1) + m_k. Verificado contra BFS en el TP 1.
export function costoMudanza(discos) {
  const grupos = [];
  for (const t of discos) {
    const ultimo = grupos[grupos.length - 1];
    if (ultimo && ultimo.p === t.priority) ultimo.n++;
    else grupos.push({ p: t.priority, n: 1 });
  }
  let c = 0;
  for (let i = grupos.length - 1; i >= 0; i--) c = 2 * c + grupos[i].n;
  return c;
}
