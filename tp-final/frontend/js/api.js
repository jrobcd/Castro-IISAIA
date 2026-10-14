// Único archivo que habla con el servidor. Mismos métodos y firmas que el objeto
// `api` del TP 1, que guardaba en localStorage: la interfaz no se enteró del cambio.
// Rechaza siempre con { status, message }, la forma del schema Error del contrato.

const BASE = '/api';

async function pedir(metodo, path, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (cuerpo !== undefined) {
    opciones.headers['Content-Type'] = 'application/json';
    opciones.body = JSON.stringify(cuerpo);
  }
  let respuesta;
  try {
    respuesta = await fetch(BASE + path, opciones);
  } catch (e) {
    throw { status: 0, message: 'No hay conexión con el servidor. ¿Está corriendo?' };
  }
  if (respuesta.status === 204) return null;
  let datos = null;
  try { datos = await respuesta.json(); } catch (e) { /* cuerpo no JSON */ }
  if (!respuesta.ok) {
    throw { status: respuesta.status, message: datos?.message || `El servidor respondió ${respuesta.status}.` };
  }
  return datos;
}

export const api = {
  listProjects: () => pedir('GET', '/projects'),
  createProject: datos => pedir('POST', '/projects', datos),
  getProject: id => pedir('GET', `/projects/${id}`),
  updateProject: (id, datos) => pedir('PATCH', `/projects/${id}`, datos),
  deleteProject: id => pedir('DELETE', `/projects/${id}`),
  listTasks: projectId => pedir('GET', `/projects/${projectId}/tasks`),
  createTask: (projectId, datos) => pedir('POST', `/projects/${projectId}/tasks`, datos),
  getTask: id => pedir('GET', `/tasks/${id}`),
  updateTask: (id, cambios) => pedir('PATCH', `/tasks/${id}`, cambios),
  deleteTask: id => pedir('DELETE', `/tasks/${id}`),
};
