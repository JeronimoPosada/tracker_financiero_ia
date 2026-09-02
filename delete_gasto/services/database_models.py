from sqlalchemy import Column, Integer, String, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ingreso(Base):
    __tablename__ = 'ingresos'

    id_ingresos = Column('id_ingresos', Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    categoria = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=True)
    metodo_ingreso = Column(String, nullable=True)

class Gasto(Base):
    __tablename__ = 'gastos'

    id_gastos = Column('id_gastos', Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    categoria = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=True)
    metodo_pago = Column(String, nullable=True)

class Meta(Base):
    __tablename__ = 'metas'

    id_metas = Column('id_metas', Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    monto_objetivo = Column(Float, nullable=False)
    monto_actual = Column(Float, nullable=False)
    fecha_limite = Column(Date, nullable=False)

# Vistas y funciones de cálculo
SaldoDisponible = func.coalesce(func.sum(Ingreso.monto), 0) - func.coalesce(func.sum(Gasto.monto), 0)

