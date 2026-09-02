from aiogram import Router, types
from aiogram.filters import Command
from delete_gasto.services.database import SessionLocal

router = Router()

@router.message(Command("ayuda"))
async def cmd_ayuda(message: types.Message):
    texto_ayuda = (
        "📊 <b>COMANDOS DISPONIBLES</b>\n\n"
        "📝 <b>Comandos principales:</b>\n"
        "/metas - Ver tus metas\n"
        "/resumen - Ver resumen de gastos\n"
        "/saldo - Ver saldo disponible\n"
        "/graficos - Ver gráfica de gastos\n"
        "/borrar_gasto [id] - Borrar un gasto\n"
        "/borrar_ingreso [id] - Borrar un ingreso\n"
        "/borrar_meta [nombre] - Borrar una meta\n"
        "/ayuda - Mostrar ayuda\n"
        "/comparar_meses - Comparar gastos entre meses\n"
        "/predecir - Predicción de IA\n"
        "/exportar - Exportar reporte financiero"
    )
    await message.answer(texto_ayuda, parse_mode="HTML")

