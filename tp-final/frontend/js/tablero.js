// Dibuja las torres. No decide nada: recibe el estado y a quién avisar de cada clic.

import { costoMudanza, pila } from './torres.js';

function el(tag, props = {}, ...hijos) {
  const nodo = Object.assign(document.createElement(tag), props);
  nodo.append(...hijos);
  return nodo;
}

function dibujarDiscos(tareas, elegida, on) {
  const contenedor = el('div', { className: 'pila' });
  const discos = pila(tareas);
  discos.forEach((t, i) => {
    const d = el('button', {
      type: 'button',
      className: 'disco' + (elegida === t.id ? ' elegido' : ''),
      textContent: t.title,
      title: `${t.title} · prioridad ${t.priority}`,
    });
    d.dataset.p = t.priority;
    d.style.width = (30 + t.priority * 13) + '%';
    const encima = discos.length - 1 - i;
    d.addEventListener('click', e => { e.stopPropagation(); on.disco(t, encima); });
    contenedor.append(d);
  });
  const costo = el('p', {
    className: 'costo',
    title: 'Mínimo de movimientos para pasar toda la torre a otra, con la tercera libre.',
    textContent: discos.length ? `Mudarla entera: ${costoMudanza(discos)} mov.` : 'Vacía',
  });
  return [contenedor, costo];
}

function dibujarHechas(tareas, on) {
  const hechas = tareas.filter(t => t.done);
  if (!hechas.length) return [];
  const ul = el('ul');
  for (const t of hechas) {
    const borrar = el('button', { type: 'button', textContent: 'borrar' });
    borrar.addEventListener('click', e => { e.stopPropagation(); on.borrarHecha(t); });
    ul.append(el('li', { textContent: t.title }, borrar));
  }
  const bloque = el('div', { className: 'hechas' }, el('strong', { textContent: `Hechas (${hechas.length})` }), ul);
  bloque.addEventListener('click', e => e.stopPropagation());
  return [bloque];
}

function dibujarTorre(p, tareas, elegida, on) {
  const torre = el('section', { className: 'torre' + (elegida !== null ? ' destino' : '') });
  torre.dataset.projectId = p.id;

  const nombre = el('input', { className: 'nombre', value: p.name });
  nombre.setAttribute('aria-label', 'Nombre del proyecto');
  nombre.addEventListener('click', e => e.stopPropagation());
  nombre.addEventListener('change', () => on.renombrar(p, nombre.value));
  torre.append(nombre, ...dibujarDiscos(tareas, elegida, on));

  if (elegida !== null) {
    const aca = el('button', { type: 'button', className: 'aca', textContent: 'Poner acá' });
    aca.addEventListener('click', e => { e.stopPropagation(); on.torre(p.id); });
    torre.append(aca);
  }
  torre.append(...dibujarHechas(tareas, on));
  torre.addEventListener('click', () => on.torre(p.id));
  return torre;
}

export function dibujar(estado, on) {
  const sel = document.querySelector('#nueva-proyecto');
  const previo = sel.value;
  sel.innerHTML = '';
  for (const p of estado.proyectos) sel.add(new Option(p.name, p.id));
  if (previo) sel.value = previo;

  const tablero = document.querySelector('#tablero');
  tablero.replaceChildren(...estado.proyectos.map(p =>
    dibujarTorre(p, estado.tareas.get(p.id) || [], estado.elegida, on)));

  document.querySelector('#acciones').classList.toggle('visible', estado.elegida !== null);
  document.querySelector('#movimientos').textContent = estado.movimientos;
}
