"""Lo que entra y lo que sale por la API. Separado de las tablas, igual que en el contrato."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel


class Entrada(BaseModel):
    # extra="forbid": un campo desconocido es 422, no se ignora (deuda 3 del TP 2).
    # strict=True: "3" no es un entero ni "true" un booleano, como dice el contrato.
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )


class Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    @field_validator("created_at", "updated_at", mode="after", check_fields=False)
    @classmethod
    def _en_utc(cls, valor: datetime) -> datetime:
        # SQLite no guarda la zona: el valor vuelve naive y se lo estampa como UTC.
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)


class ProjectInput(Entrada):
    name: str = Field(min_length=1, max_length=60)


class ProjectOut(Salida):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class TaskInput(Entrada):
    title: str = Field(min_length=1, max_length=120)
    priority: int = Field(ge=1, le=5)


class TaskPatch(Entrada):
    # Sin "| None": un null explícito es 422. El default no se valida, así que
    # un campo ausente queda en None y no figura en model_fields_set.
    title: str = Field(default=None, min_length=1, max_length=120)
    priority: int = Field(default=None, ge=1, le=5)
    done: bool = None
    project_id: int = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _no_vacio(self):
        # Deuda 2 del TP 2: un PATCH vacío no puede tocar updatedAt.
        if not self.model_fields_set:
            raise ValueError("El cuerpo tiene que traer al menos un campo.")
        return self


class TaskOut(Salida):
    id: int
    project_id: int
    title: str
    priority: int
    done: bool
    created_at: datetime
    updated_at: datetime


class ErrorOut(BaseModel):
    status: int
    message: str
