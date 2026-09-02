from aiogram import Router
from sqlalchemy.orm import Session
from sqlalchemy import func
from delete_gasto.services.database_models import Gasto, Meta


def resumen_gastos_por_categoria(db: Session):
    """
    Devuelve un diccionario {categoria: total_gastado} 
    sobre todos los gastos registrados en la DB.
    """
    result = db.query(
        Gasto.categoria, 
        func.sum(Gasto.monto).label('total')
    ).group_by(Gasto.categoria).all()
    
    return {row.categoria: float(row.total) for row in result}

def progreso_todas_las_metas(db: Session):
    """
    Devuelve una lista de diccionarios con el progreso de cada meta.
    """
    metas = db.query(Meta).all()
    resultado = []
    
    for m in metas:
        porcentaje = (m.monto_actual / m.monto_objetivo * 100) if m.monto_objetivo > 0 else 0
        resultado.append({
            "nombre": m.nombre,
            "objetivo": m.monto_objetivo,
            "actual": m.monto_actual,
            "porcentaje": round(porcentaje, 2),
            "fecha_limite": str(m.fecha_limite)
        })
    
    return resultado

def transacciones_recientes(db: Session, limite: int = 10):
    """
    Devuelve los últimos 'limite' gastos registrados.
    """
    recientes = db.query(Gasto).order_by(Gasto.fecha.desc()).limit(limite).all()
    return recientes

