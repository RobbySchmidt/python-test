from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import Column, JSON  # ✅ Import Column and JSON
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Database Models ----------

class Collection(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str


class FieldDef(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    collection_id: str = Field(foreign_key="collection.id")
    name: str
    type: str  # "string", "boolean", "number", etc.


class Record(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    collection_id: str = Field(foreign_key="collection.id")
    data: dict = Field(sa_column=Column(JSON))  # ✅ Store dict as JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------- Database Setup ----------

sqlite_url = "sqlite:///./db.sqlite"
engine = create_engine(sqlite_url, echo=False)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# ---------- API Routes ----------

# Collections
@app.get("/collections", response_model=List[Collection])
def list_collections():
    with Session(engine) as session:
        return session.exec(select(Collection)).all()

@app.post("/collections", response_model=Collection)
def create_collection(collection: Collection):
    with Session(engine) as session:
        session.add(collection)
        session.commit()
        session.refresh(collection)
        return collection


# Fields
@app.get("/collections/{collection_id}/fields", response_model=List[FieldDef])
def get_fields(collection_id: str):
    with Session(engine) as session:
        return session.exec(select(FieldDef).where(FieldDef.collection_id == collection_id)).all()

@app.post("/collections/{collection_id}/fields", response_model=FieldDef)
def add_field(collection_id: str, field: FieldDef):
    field.collection_id = collection_id
    with Session(engine) as session:
        session.add(field)
        session.commit()
        session.refresh(field)
        return field


# Records
@app.get("/collections/{collection_id}/records", response_model=List[Record])
def get_records(collection_id: str):
    with Session(engine) as session:
        return session.exec(select(Record).where(Record.collection_id == collection_id)).all()

@app.post("/collections/{collection_id}/records", response_model=Record)
def create_record(collection_id: str, record: Record):
    record.collection_id = collection_id
    with Session(engine) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

@app.patch("/records/{record_id}", response_model=Record)
def update_record(record_id: str, updated: Record):
    with Session(engine) as session:
        record = session.get(Record, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        record.data = updated.data
        session.commit()
        session.refresh(record)
        return record

@app.delete("/records/{record_id}")
def delete_record(record_id: str):
    with Session(engine) as session:
        record = session.get(Record, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        session.delete(record)
        session.commit()
        return {"message": "Deleted"}
