from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from tda_cola import Cola


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


colas_por_personaje = {}

# --- Endpoints ---

@app.post("/personajes", response_model=schemas.Personaje)
def crear_personaje(personaje: schemas.PersonajeCreate, db: Session = Depends(get_db)):
    db_personaje = models.Personaje(**personaje.dict())
    db.add(db_personaje)
    db.commit()
    db.refresh(db_personaje)
    colas_por_personaje[db_personaje.id] = Cola()
    return db_personaje

@app.post("/misiones", response_model=schemas.Mision)
def crear_mision(mision: schemas.MisionCreate, db: Session = Depends(get_db)):
    db_mision = models.Mision(**mision.dict())
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)
    return db_mision

@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).get(personaje_id)
    mision = db.query(models.Mision).get(mision_id)

    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrados")

    personaje.misiones.append(mision)
    db.commit()

    if personaje_id not in colas_por_personaje:
        colas_por_personaje[personaje_id] = Cola()
    colas_por_personaje[personaje_id].enqueue(mision.id)

    return {"mensaje": "Misión aceptada"}

@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(get_db)):
    cola = colas_por_personaje.get(personaje_id)
    if not cola or cola.is_empty():
        raise HTTPException(status_code=400, detail="No hay misiones en cola")

    mision_id = cola.dequeue()
    mision = db.query(models.Mision).get(mision_id)
    personaje = db.query(models.Personaje).get(personaje_id)

    personaje.experiencia += mision.experiencia
    db.commit()

    return {"mensaje": f"Misión '{mision.nombre}' completada", "xp_ganada": mision.experiencia}

@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones_en_cola(personaje_id: int):
    cola = colas_por_personaje.get(personaje_id)
    if not cola:
        raise HTTPException(status_code=404, detail="No se encontró cola para el personaje")
    return {"misiones_en_orden": cola.items}
