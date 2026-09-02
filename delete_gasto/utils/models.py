from datetime import date
from pydantic import BaseModel


class Gasto(BaseModel):
    fecha: date
    categoria: str
    monto: float
    descripcion: str
    metodo_pago: str

class Ingreso(BaseModel):
    fecha: date
    categoria: str
    monto: float
    descripcion: str
    metodo_ingreso: str          # "Efectivo", "Tarjeta"

class Meta(BaseModel):
    nombre: str
    descripcion: str    
    monto_objetivo: float
    monto_actual: float
    fecha_limite: date

