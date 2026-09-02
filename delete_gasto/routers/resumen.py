from aiogram import types, Router
from aiogram.filters import Command
from delete_gasto.services.database import SessionLocal
from delete_gasto.routers.analisis import (
    resumen_gastos_por_categoria, 
    progreso_todas_las_metas
)
router = Router()
@router.message(Command("resumen"))
async def cmd_resumen(message: types.Message):
    db = SessionLocal()
    try:
        resumen = resumen_gastos_por_categoria(db)
        if not resumen:
            await message.answer("📊 Aún no tienes gastos registrados. ¡Usa el bot para registrar tu primera movimiento!")
            return
        
        texto = "📊 *Resumen de Gastos por Categoría*\n\n"
        for categoria, total in resumen.items():
            texto += f"• {categoria}: ${total:,.0f}\n"
            
        total_general = sum(resumen.values())
        texto += f"\n💰 *Total General Gastado*: ${total_general:,.0f}"
        await message.answer(texto, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Error al generar el resumen: {e}")
    finally:
        db.close()


