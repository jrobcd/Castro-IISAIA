"""Engine de SQLite y una sesión por request."""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///tareas.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(engine, expire_on_commit=False)


@event.listens_for(engine, "connect")
def _activar_foreign_keys(conexion, _registro):
    # SQLite no las controla salvo que se le pida, conexión por conexión.
    conexion.execute("PRAGMA foreign_keys = ON")


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db
