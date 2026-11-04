"""Startet die API. Die fünf CRUD-Funktionen werden für jede Tabelle registriert."""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

import models as m

engine = create_engine(
    os.getenv("DATABASE_URL", "postgresql+psycopg://hospital:hospital@db:5432/hospital"),
    pool_pre_ping=True,
)


@asynccontextmanager
async def lifespan(app):
    m.Base.metadata.create_all(engine)
    yield
    engine.dispose()


app = FastAPI(title="Hospital — Minimal", lifespan=lifespan)


def get_db():
    with Session(engine) as db:
        yield db


@app.exception_handler(IntegrityError)
async def constraint_error(request, exception):
    return JSONResponse(status_code=409, content={
        "detail": "Doppelter Wert oder Konflikt mit einer Datenbankbeziehung."
    })


@app.exception_handler(DataError)
async def data_error(request, exception):
    return JSONResponse(status_code=422, content={"detail": "Ungültiger Datenbankwert."})


def as_dict(record):
    return {column.key: getattr(record, column.key) for column in inspect(type(record)).columns}


def read_record(db, model, item_id):
    columns = inspect(model).primary_key
    parts = item_id.split(",")
    try:
        if len(parts) != len(columns):
            raise ValueError()
        key = tuple(column.type.python_type(value) for column, value in zip(columns, parts))
    except (ValueError, TypeError):
        raise HTTPException(422, "Ungültiger Schlüssel.") from None
    record = db.get(model, key[0] if len(key) == 1 else key)
    if record is None:
        raise HTTPException(404, "Datensatz nicht gefunden.")
    return record


def validate_data(model, data, creating=False):
    columns = {column.key: column for column in inspect(model).columns}
    if not data or data.keys() - columns.keys():
        raise HTTPException(422, "Leeres JSON oder unbekannte Felder.")
    result = {}
    for name, value in data.items():
        column = columns[name]
        if column.identity is not None:
            raise HTTPException(422, "Numerische IDs vergibt die Datenbank.")
        if not creating and column.primary_key and len(inspect(model).primary_key) == 1:
            raise HTTPException(422, "Der Primärschlüssel kann nicht geändert werden.")
        if value is None:
            if not column.nullable:
                raise HTTPException(422, f"{name} ist ein Pflichtfeld.")
        else:
            try:
                value = TypeAdapter(column.type.python_type).validate_python(value)
            except ValidationError:
                raise HTTPException(422, f"{name}: ungültiger Datentyp.") from None
            if isinstance(value, str) and column.type.length is not None:
                if len(value) > column.type.length:
                    raise HTTPException(422, f"{name}: maximal {column.type.length} Zeichen.")
        result[name] = value
    if creating:
        required = {column.key for column in columns.values()
                    if not column.nullable and column.identity is None}
        if missing := required - result.keys():
            raise HTTPException(422, f"Pflichtfelder fehlen: {', '.join(sorted(missing))}")
    return result


def register_crud(path, model):
    prefix = f"/{path}"

    @app.post(prefix, status_code=201, tags=[path], name=f"{path}_create")
    def create(data: dict, db: Session = Depends(get_db)):
        record = model(**validate_data(model, data, creating=True))
        db.add(record)
        db.commit()
        db.refresh(record)
        return as_dict(record)

    @app.get(prefix, tags=[path], name=f"{path}_list")
    def read_all(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
                 db: Session = Depends(get_db)):
        query = select(model).order_by(*inspect(model).primary_key).offset(offset).limit(limit)
        return [as_dict(record) for record in db.scalars(query)]

    @app.get(prefix + "/{item_id}", tags=[path], name=f"{path}_read")
    def read_one(item_id: str, db: Session = Depends(get_db)):
        return as_dict(read_record(db, model, item_id))

    @app.patch(prefix + "/{item_id}", tags=[path], name=f"{path}_update")
    def update(item_id: str, data: dict, db: Session = Depends(get_db)):
        record = read_record(db, model, item_id)
        for name, value in validate_data(model, data).items():
            setattr(record, name, value)
        db.commit()
        db.refresh(record)
        return as_dict(record)

    @app.delete(prefix + "/{item_id}", status_code=204, tags=[path], name=f"{path}_delete")
    def delete(item_id: str, db: Session = Depends(get_db)):
        db.delete(read_record(db, model, item_id))
        db.commit()
        return Response(status_code=204)


TABLES = {
    "pacientes": m.Paciente,
    "atendentes": m.Atendente,
    "profissionais-saude": m.ProfissionalSaude,
    "estagiarios": m.Estagiario,
    "estabelecimentos-saude": m.EstabelecimentoSaude,
    "medicamentos": m.Medicamento,
    "condicoes-saude": m.CondicaoSaude,
    "tipos-parametro": m.TipoParametro,
    "consultas": m.Consulta,
    "agendamentos-medicao": m.AgendamentoMedicao,
    "agendamentos-parametros": m.AgendamentoParametro,
    "medicoes-clinicas": m.MedicaoClinica,
    "resultados-exame": m.ResultadoExame,
    "pacientes-condicoes": m.PacienteCondicao,
    "usos-medicamento": m.UsoMedicamento,
    "reacoes-alergicas": m.ReacaoAlergica,
}

for path, model in TABLES.items():
    register_crud(path, model)
