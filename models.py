from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Relación muchos a muchos: personajes y misiones
personaje_mision = Table(
    'personaje_mision',
    Base.metadata,
    Column('personaje_id', Integer, ForeignKey('personajes.id')),
    Column('mision_id', Integer, ForeignKey('misiones.id'))
)

class Personaje(Base):
    __tablename__ = 'personajes'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    nivel = Column(Integer)
    experiencia = Column(Integer, default=0)

    misiones = relationship("Mision", secondary=personaje_mision, back_populates="personajes")

class Mision(Base):
    __tablename__ = 'misiones'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    descripcion = Column(String)
    experiencia = Column(Integer)

    personajes = relationship("Personaje", secondary=personaje_mision, back_populates="misiones")
