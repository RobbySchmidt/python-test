from fastapi import FastAPI, HTTPException # FastAPI = the web framework (like Nuxt but backend).
from fastapi.middleware.cors import CORSMiddleware # allows your Nuxt frontend to talk to your FastAPI backend.
from sqlmodel import SQLModel, Field, create_engine, Session, select # handles models + database interaction (similar to using an ORM like Prisma). / SQLite = your local database.
from sqlalchemy import Column, JSON
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
from sqlmodel import delete

app = FastAPI() #Creates your FastAPI application instance, like createNuxtApp() in Nuxt.

# CORS for frontend

# Lets your frontend (localhost:3000) make HTTP requests to this backend.
# Similar to Nuxt's server middleware for handling CORS or using @nuxt/http.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Database Models ----------

# Represents a "Collection" (like a content type or table).
# Each gets a unique id and a name.
class Collection(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str


# Represents a field in a collection (e.g., "title", "price").
# Has a collection_id to associate it with a Collection.
class FieldDef(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    collection_id: str = Field(foreign_key="collection.id")
    name: str
    type: str  # "string", "boolean", "number", etc.


# A row in a collection, storing its actual data as JSON.
# Like storing dynamic form data (a flexible schema).
class Record(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    collection_id: str = Field(foreign_key="collection.id")
    data: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------- Database Setup ----------

# SQLite is used as your database.
sqlite_url = "sqlite:///./db.sqlite"
engine = create_engine(sqlite_url, echo=False)


# On app start, it creates the tables based on your model classes (Collection, FieldDef, Record).
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# ---------- API Routes ----------

# Collections

# Returns all collections from the database.
@app.get("/collections", response_model=List[Collection])
def list_collections():
    with Session(engine) as session:
        return session.exec(select(Collection)).all()


# Adds a new collection.
@app.post("/collections", response_model=Collection)
def create_collection(collection: Collection):
    with Session(engine) as session:
        session.add(collection)
        session.commit()
        session.refresh(collection)
        return collection


# Deletes a collection and all its fields and records (cleans up related data).
# Equivalent to a cascade delete.
@app.delete("/collections/{collection_id}")
def delete_collection(collection_id: str):
    with Session(engine) as session:
        collection = session.get(Collection, collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        # delete related fields and records if you want to clean up the DB
        session.exec(delete(FieldDef).where(FieldDef.collection_id == collection_id))
        session.exec(delete(Record).where(Record.collection_id == collection_id))
        
        session.delete(collection)
        session.commit()
        return {"message": "Collection deleted"}


# Fields

# Gets all fields (like "title", "description") for a specific collection.
@app.get("/collections/{collection_id}/fields", response_model=List[FieldDef])
def get_fields(collection_id: str):
    with Session(engine) as session:
        return session.exec(select(FieldDef).where(FieldDef.collection_id == collection_id)).all()


# Adds a new field definition (e.g., a new column).
@app.post("/collections/{collection_id}/fields", response_model=FieldDef)
def add_field(collection_id: str, field: FieldDef):
    field.collection_id = collection_id
    with Session(engine) as session:
        session.add(field)
        session.commit()
        session.refresh(field)
        return field


# Deletes a single field from a collection.
@app.delete("/collections/{collection_id}/fields/{field_id}")
def delete_field(collection_id: str, field_id: str):
    with Session(engine) as session:
        field = session.get(FieldDef, field_id)
        if not field or field.collection_id != collection_id:
            raise HTTPException(status_code=404, detail="Field not found")
        session.delete(field)
        session.commit()
        return {"message": "Field deleted successfully"}



# Records

# Retrieves all entries (rows) for a given collection.
@app.get("/collections/{collection_id}/records", response_model=List[Record])
def get_records(collection_id: str):
    with Session(engine) as session:
        return session.exec(select(Record).where(Record.collection_id == collection_id)).all()


# Adds a new record with JSON data.
@app.post("/collections/{collection_id}/records", response_model=Record)
def create_record(collection_id: str, record: Record):
    record.collection_id = collection_id
    with Session(engine) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


# Updates a record’s data field (partial update).
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


# Deletes one record by ID.
@app.delete("/records/{record_id}")
def delete_record(record_id: str):
    with Session(engine) as session:
        record = session.get(Record, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        session.delete(record)
        session.commit()
        return {"message": "Deleted"}