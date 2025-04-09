from pydantic import BaseModel
from typing import List, Optional

class MisionBase(BaseModel):
    nombre: str
    descripcion: str
    experiencia: int

class MisionCreate(MisionBase):
    pass

class Mision(MisionBase):
    id: int
    class Config:
        orm_mode = True

class PersonajeBase(BaseModel):
    nombre: str
    nivel: int
    experiencia: int = 0

class PersonajeCreate(PersonajeBase):
    pass

class Personaje(PersonajeBase):
    id: int
    misiones: List[Mision] = []
    class Config:
        orm_mode = True
