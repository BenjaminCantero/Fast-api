from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tda_cola import Cola

app = FastAPI()

# Base de datos simulada
personajes_db = {}
misiones_db = {}
misiones_por_personaje = {}

# Modelos
class Personaje(BaseModel):
    nombre: str
    nivel: int = 1
    experiencia: int = 0

class Mision(BaseModel):
    nombre: str
    descripcion: str
    experiencia: int

# --- Endpoints CRUD básicos ---
@app.post("/personajes")
def crear_personaje(p: Personaje):
    nuevo_id = max(personajes_db.keys(), default=0) + 1
    personajes_db[nuevo_id] = p.dict()
    misiones_por_personaje[nuevo_id] = Cola()
    return {"id": nuevo_id, "personaje": personajes_db[nuevo_id]}

@app.post("/misiones")
def crear_mision(m: Mision):
    nuevo_id = max(misiones_db.keys(), default=0) + 1
    misiones_db[nuevo_id] = m.dict()
    return {"id": nuevo_id, "mision": misiones_db[nuevo_id]}

# --- Aceptar misión (encolar) ---
@app.post("/personajes/{id_personaje}/misiones/{id_mision}")
def aceptar_mision(id_personaje: int, id_mision: int):
    if id_personaje not in personajes_db or id_mision not in misiones_db:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrada")
    mision = {"id": id_mision, **misiones_db[id_mision]}
    misiones_por_personaje[id_personaje].enqueue(mision)
    return {"mensaje": "Misión aceptada", "mision": mision}

# --- Completar misión (desencolar) ---
@app.post("/personajes/{id_personaje}/completar")
def completar_mision(id_personaje: int):
    if id_personaje not in personajes_db:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    cola = misiones_por_personaje[id_personaje]
    if cola.is_empty():
        raise HTTPException(status_code=400, detail="No hay misiones por completar")
    
    mision_completada = cola.dequeue()
    personajes_db[id_personaje]["experiencia"] += mision_completada["experiencia"]
    return {
        "mensaje": "Misión completada",
        "mision": mision_completada,
        "experiencia_total": personajes_db[id_personaje]["experiencia"]
    }

# --- Listar misiones de un personaje ---
@app.get("/personajes/{id_personaje}/misiones")
def listar_misiones(id_personaje: int):
    if id_personaje not in personajes_db:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    cola = misiones_por_personaje[id_personaje]
    return {"misiones": cola.items}
