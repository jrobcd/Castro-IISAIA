// Estado y eventos. Acá se aplican las reglas de Hanói antes de pedirle algo a la API.

import { api } from './api.js';
import { dibujar } from './tablero.js';
import { cima, entra } from './torres.js';

// La interfaz muestra tres torres. El servidor acepta N proyectos y no sabe de este número.
const NOMBRES_INICIALES = ['Trabajo', 'Facultad', 'Casa'];
const KEY_MOVS = 'tareas-en-torre-movimientos';

const $ = sel => document.querySelector(sel);
// elegidaEn: la torre de la que se levantó. Con otra pestaña de por medio, la tarea
// puede haberse mudado mientras estaba levantada.
const estado = { proyectos: [], tareas: new Map(), elegida: null, elegidaEn: null, movimientos: leerMovimientos() };

// El contador es de esta interfaz, no un dato del sistema: queda en el navegador.
function leerMovimientos() {
  try { return Number(localStorage.getItem(KEY_MOVS)) || 0; } catch (e) { return 0; }
}
function sumarMovimiento() {
  estado.movimientos++;
  try { localStorage.setItem(KEY_MOVS, String(estado.movimientos)); } catch (e) { /* sin storage */ }
}

function avisar(texto, tipo = '') {
  const m = $('#mensaje');
  m.textContent = texto;
  m.className = tipo;
}

const tareasDe = projectId => estado.tareas.get(projectId) || [];

function tareaPorId(id) {
  for (const lista of estado.tareas.values()) {
    const t = lista.find(x => x.id === id);
    if (t) return t;
  }
  return null;
}

// Una operación a la vez. Si la API rechaza algo, se vuelve a leer todo: la
// pantalla nunca muestra un estado que el servidor no aceptó.
let enCurso = false;
async function ocupado(fn) {
  if (enCurso) return;
  enCurso = true;
  document.body.classList.add('ocupado');
  try { return await fn(); }
  catch (err) {
    avisar(err && err.message ? err.message : 'Algo falló.', 'error');
    try { await recargar(); } catch (e) { /* ya avisamos */ }
  }
  finally { enCurso = false; document.body.classList.remove('ocupado'); }
}

async function recargar() {
  estado.proyectos = (await api.listProjects()).slice(0, NOMBRES_INICIALES.length);
  const listas = await Promise.all(estado.proyectos.map(p => api.listTasks(p.id)));
  estado.tareas = new Map(estado.proyectos.map((p, i) => [p.id, listas[i]]));
  // Si la tarea levantada ya no está arriba de la torre de la que salió (se apiló otra
  // encima, o la movió otra pestaña), se suelta.
  const t = estado.elegida !== null ? tareaPorId(estado.elegida) : null;
  if (!t || t.done || t.projectId !== estado.elegidaEn || cima(tareasDe(t.projectId))?.id !== t.id) estado.elegida = null;
  dibujar(estado, manejadores);
}

function soltar(texto = '') {
  estado.elegida = null;
  avisar(texto);
  dibujar(estado, manejadores);
}

function tocarDisco(t, encima) {
  if (encima > 0) {
    const n = encima === 1 ? '1 tarea' : `${encima} tareas`;
    avisar(`"${t.title}" tiene ${n} encima. Solo se toca la de arriba.`, 'error');
    return;
  }
  if (estado.elegida === t.id) return soltar();
  if (estado.elegida !== null) return tocarTorre(t.projectId);
  estado.elegida = t.id;
  estado.elegidaEn = t.projectId;
  avisar(`"${t.title}" levantada. Elegí la torre de destino.`);
  dibujar(estado, manejadores);
}

function tocarTorre(projectId) {
  if (estado.elegida === null) return;
  const t = tareaPorId(estado.elegida);
  if (!t || t.projectId === projectId) return soltar();
  if (!entra(t, tareasDe(projectId))) {
    const arriba = cima(tareasDe(projectId));
    avisar(`No entra: "${t.title}" (prioridad ${t.priority}) no puede ir sobre "${arriba.title}" (prioridad ${arriba.priority}).`, 'error');
    return;
  }
  ocupado(async () => {
    await api.updateTask(t.id, { projectId });
    sumarMovimiento();
    estado.elegida = null;
    avisar('');
    await recargar();
  });
}

const manejadores = {
  disco: tocarDisco,
  torre: tocarTorre,
  renombrar: (p, nombre) => ocupado(async () => { await api.updateProject(p.id, { name: nombre }); await recargar(); }),
  borrarHecha: t => ocupado(async () => { await api.deleteTask(t.id); await recargar(); }),
};

function accionSobreElegida(fn, mensaje, tipo) {
  const t = tareaPorId(estado.elegida);
  if (!t) return;
  ocupado(async () => {
    await fn(t);
    estado.elegida = null;
    avisar(mensaje(t), tipo);
    await recargar();
  });
}

$('#btn-soltar').addEventListener('click', () => soltar());
$('#btn-completar').addEventListener('click', () =>
  accionSobreElegida(t => api.updateTask(t.id, { done: true }), t => `"${t.title}" completada.`, 'ok'));
$('#btn-borrar').addEventListener('click', () =>
  accionSobreElegida(t => api.deleteTask(t.id), t => `"${t.title}" borrada.`));

$('#form-nueva').addEventListener('submit', e => {
  e.preventDefault();
  const title = $('#nueva-titulo').value;
  const priority = Number($('#nueva-prioridad').value);
  const projectId = Number($('#nueva-proyecto').value);
  const arriba = cima(tareasDe(projectId));
  if (arriba && priority > arriba.priority) {
    avisar(`No entra: arriba de esa torre está "${arriba.title}" (prioridad ${arriba.priority}). Elegí otra torre o liberá esa.`, 'error');
    return;
  }
  ocupado(async () => {
    await api.createTask(projectId, { title, priority });
    $('#nueva-titulo').value = '';
    avisar('Apilada.', 'ok');
    await recargar();
  });
});

// Con un servidor de por medio, otra pestaña puede haber cambiado algo.
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') ocupado(recargar);
});

ocupado(async () => {
  const proyectos = await api.listProjects();
  for (const nombre of NOMBRES_INICIALES.slice(proyectos.length)) await api.createProject({ name: nombre });
  await recargar();
});
