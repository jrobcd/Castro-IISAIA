"""Las diez operaciones del contrato. Los nombres de las funciones son los operationId."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models import Project, Task, ahora
from backend.schemas import ProjectInput, ProjectOut, TaskInput, TaskOut, TaskPatch

router = APIRouter()

Db = Annotated[Session, Depends(get_db)]
ProjectId = Annotated[int, Path(alias="projectId")]
TaskId = Annotated[int, Path(alias="taskId")]


def _proyecto(db: Session, project_id: int) -> Project:
    proyecto = db.get(Project, project_id)
    if proyecto is None:
        raise HTTPException(404, "El proyecto no existe.")
    return proyecto


def _tarea(db: Session, task_id: int) -> Task:
    tarea = db.get(Task, task_id)
    if tarea is None:
        raise HTTPException(404, "La tarea no existe.")
    return tarea


# --- Proyectos ---------------------------------------------------------------

@router.get("/projects", response_model=list[ProjectOut])
def listProjects(db: Db):
    return db.scalars(select(Project).order_by(Project.id)).all()


@router.post("/projects", status_code=201, response_model=ProjectOut)
def createProject(datos: ProjectInput, db: Db, response: Response):
    t0 = ahora()
    proyecto = Project(name=datos.name, created_at=t0, updated_at=t0)
    db.add(proyecto)
    db.commit()
    response.headers["Location"] = f"/api/projects/{proyecto.id}"
    return proyecto


@router.get("/projects/{projectId}", response_model=ProjectOut)
def getProject(project_id: ProjectId, db: Db):
    return _proyecto(db, project_id)


@router.patch("/projects/{projectId}", response_model=ProjectOut)
def updateProject(project_id: ProjectId, datos: ProjectInput, db: Db):
    proyecto = _proyecto(db, project_id)
    proyecto.name = datos.name
    proyecto.updated_at = ahora()
    db.commit()
    return proyecto


@router.delete("/projects/{projectId}", status_code=204)
def deleteProject(project_id: ProjectId, db: Db):
    proyecto = _proyecto(db, project_id)
    tareas = select(Task).where(Task.project_id == project_id)
    if db.scalars(tareas.where(Task.done.is_(False))).first() is not None:
        raise HTTPException(409, "El proyecto tiene tareas pendientes.")
    # Primero las tareas y en una sentencia propia: sin relationship declarada, el
    # unit of work de SQLAlchemy no sabe que van antes y puede borrar el proyecto
    # primero, lo que viola la foreign key.
    db.execute(delete(Task).where(Task.project_id == project_id))
    db.delete(proyecto)
    db.commit()
    return Response(status_code=204)


# --- Tareas ------------------------------------------------------------------

@router.get("/projects/{projectId}/tasks", response_model=list[TaskOut])
def listTasks(project_id: ProjectId, db: Db, done: bool | None = None):
    _proyecto(db, project_id)
    consulta = select(Task).where(Task.project_id == project_id).order_by(Task.id)
    if done is not None:
        consulta = consulta.where(Task.done == done)
    return db.scalars(consulta).all()


@router.post("/projects/{projectId}/tasks", status_code=201, response_model=TaskOut)
def createTask(project_id: ProjectId, datos: TaskInput, db: Db, response: Response):
    _proyecto(db, project_id)
    t0 = ahora()
    tarea = Task(project_id=project_id, title=datos.title, priority=datos.priority,
                 done=False, created_at=t0, updated_at=t0)
    db.add(tarea)
    db.commit()
    response.headers["Location"] = f"/api/tasks/{tarea.id}"
    return tarea


@router.get("/tasks/{taskId}", response_model=TaskOut)
def getTask(task_id: TaskId, db: Db):
    return _tarea(db, task_id)


@router.patch("/tasks/{taskId}", response_model=TaskOut)
def updateTask(task_id: TaskId, datos: TaskPatch, db: Db):
    tarea = _tarea(db, task_id)
    cambios = datos.model_dump(include=datos.model_fields_set)
    # Deuda 1 del TP 2: el proyecto destino viene en el body, así que si no existe es 422.
    if "project_id" in cambios and db.get(Project, cambios["project_id"]) is None:
        raise HTTPException(422, "El proyecto destino no existe.")
    for campo, valor in cambios.items():
        setattr(tarea, campo, valor)
    tarea.updated_at = ahora()
    db.commit()
    return tarea


@router.delete("/tasks/{taskId}", status_code=204)
def deleteTask(task_id: TaskId, db: Db):
    db.delete(_tarea(db, task_id))
    db.commit()
    return Response(status_code=204)
