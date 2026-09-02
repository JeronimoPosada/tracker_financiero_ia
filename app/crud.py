from sqlalchemy.orm import Session
from delete_gasto.services.database_models import Ingreso, Gasto, Meta
from delete_gasto.utils.models import Ingreso as IngresoModel, Gasto as GastoModel, Meta as MetaModel

def crear_ingreso(db: Session, ingreso: IngresoModel):
    # Convertimos el modelo de Pydantic a un objeto del modelo ORM de SQLAlchemy
    db_ingreso = Ingreso(
        fecha=ingreso.fecha,
        categoria=ingreso.categoria,
        monto=ingreso.monto,
        descripcion=ingreso.descripcion,
        metodo_ingreso=ingreso.metodo_ingreso
    )

    # Lo agregamos a al sesión, lo guardamos (commit) y refrescamos para obtener el ID generado
    db.add(db_ingreso)
    db.commit()
    db.refresh(db_ingreso)
    return db_ingreso

def eliminar_ingreso(db: Session, id_ingresos: int):
    ingreso = db.query(Ingreso).filter(Ingreso.id_ingresos == id_ingresos).first()
    if ingreso:
        db.delete(ingreso)
        db.commit()
        return True
    return False

def crear_gasto(db: Session, gasto: GastoModel):
    db_gasto = Gasto(
        fecha=gasto.fecha,
        categoria=gasto.categoria,
        monto=gasto.monto,
        descripcion=gasto.descripcion,
        metodo_pago=gasto.metodo_pago
    )
    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    return db_gasto

def eliminar_gasto(db: Session, id_gastos: int): 
    gasto = db.query(Gasto).filter(Gasto.id_gastos == id_gastos).first()
    if gasto:
        db.delete(gasto)
        db.commit()
        return True
    return False

def crear_meta(db: Session, meta: MetaModel):   
    db_meta = Meta(
        nombre=meta.nombre,
        descripcion=meta.descripcion,
        monto_objetivo=meta.monto_objetivo,
        monto_actual=meta.monto_actual,
        fecha_limite=meta.fecha_limite
    )
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    return db_meta

def eliminar_meta(db: Session, meta: MetaModel):
    meta = db.query(Meta).filter(Meta.nombre == meta.nombre).first()
    if meta:
        db.delete(meta)
        db.commit()
        return True
    return False

def obtener_meta(db: Session):
    return db.query(Meta).all()

def abonar_meta(db: Session, meta: MetaModel, monto:float):
    meta = db.query(Meta).filter(Meta.nombre == meta.nombre).first()
    if meta:
        meta.monto_actual += monto
        db.commit()
        db.refresh(meta)
        return meta
    return None

def buscar_meta_por_nombre(db:Session, nombre:str):
    # ilike permite buscar sin importar mayúsculas o minúsculas
    return db.query(Meta).filter(Meta.nombre.ilike(f"%{nombre}")).first()


