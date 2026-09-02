
from aiogram import types, Router
from aiogram.filters import Command
from sqlalchemy import func
from delete_gasto.services.database import SessionLocal
from delete_gasto.services.database_models import Gasto as GastoORM, Ingreso as IngresoORM

router = Router()


@router.message(Command("saldo"))
async def cmd_saldo(message: types.Message):
    """Muestra el saldo actual: total ingresos - total gastos"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        from delete_gasto.services.database_models import Ingreso, Gasto
        
        # Calcular totales
        total_ingresos = db.query(func.sum(Ingreso.monto)).scalar() or 0
        total_gastos = db.query(func.sum(Gasto.monto)).scalar() or 0
        saldo = float(total_ingresos) - float(total_gastos)
        
        # Usar HTML en lugar de Markdown para evitar error de parsing de entidades
        texto = "<b>💰 SALDO ACTUAL</b>"
        texto += "\n\n💵 Ingresos totales: $" + str(total_ingresos)
        texto += "\n💸 Gastos totales: $" + str(total_gastos)
        texto += "\n💳 <b>Saldo disponible: $" + str(saldo) + "</b>"
        texto += "\n\nUsa /comparar_meses para ver gráficas detalladas."
        
        await message.answer(texto, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Error calculando saldo: {e}")
    finally:
        db.close()