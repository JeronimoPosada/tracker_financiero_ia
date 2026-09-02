from aiogram import Router, types
from aiogram.filters import Command
from delete_gasto.services.database import SessionLocal
from app.crud import obtener_meta
from delete_gasto.utils.barra_progeso import generar_barra_progreso
from delete_gasto.routers.analisis import progreso_todas_las_metas

router = Router()

@router.message(Command("metas"))
async def cmd_listar_metas(message: types.Message):
    db = SessionLocal()
    try:
        metas = obtener_meta(db)
        if not metas:
            await message.answer("🎯 No tienes metas activas todavía. Crea una diciendo por ejemplo: 'Quiero ahorrar 500 mil pal viaje antes de diciembre'")
            return
        texto_metas = "🎯 *TUS METAS FINANCIERAS:*\n\n"
        for m in metas:
            porcentaje = (m.monto_actual / m.monto_objetivo * 100) if m.monto_objetivo > 0 else 0
            barra = generar_barra_progreso(m.monto_actual, m.monto_objetivo)
            texto_metas += (
                f"📌 {m.nombre}\n"
                f"💰 ${m.monto_actual:,.0f} / ${m.monto_objetivo:,.0f} ({porcentaje:.1f}%)\n"
                f"[{barra}]\n"
                f"📅 Límite: {m.fecha_limite}\n\n"
            )
        await message.answer(texto_metas, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Error consultando metas: {e}")
    finally:
        db.close()

@router.message(Command("metas_analaticas"))
async def cmd_metas_analaticas(message: types.Message):
    db = SessionLocal()
    try:
        metas = progreso_todas_las_metas(db)
        if not metas:
            await message.answer("🎯 No tienes metas activas. Crea una diciendo: 'Quiero ahorrar X pal Y antes de Z'.")
            return

        texto = "🎯 *Progreso Detallado de tus Metas*\n\n"
        for m in metas:
            barra_visual = "█" * int(m["porcentaje"]/10) + "░" * (10 - int(m["porcentaje"]/10))
            texto += (
                f"📌 {m['nombre']}\n"
                f"💰 ${m['actual']:,.0f} / ${m['objetivo']:,.0f} ({m['porcentaje']}%)\n"
                f"📅 Vence: {m['fecha_limite']}\n"
                f"[{barra_visual}]\n\n"
            )
        await message.answer(texto, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Error consultando metas: {e}")
    finally:
        db.close()






