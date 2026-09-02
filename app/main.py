import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

# Importaciones de servicios y utilidades
from delete_gasto.services.database import SessionLocal
from delete_gasto.services.ai_parser import procesar_mensaje_financiero
from delete_gasto.services.database import SessionLocal
from delete_gasto.utils.models import Gasto as GastoSchema, Ingreso as IngresoSchema, Meta as MetaSchema
from aiogram.types import BotCommand
from delete_gasto.services.sheets_service import (
    registrar_en_sheets, 
    registrar_meta_en_sheets, 
    eliminar_de_sheets, 
    sincronizar_todas_las_metas_con_sheets
)
from delete_gasto.utils.barra_progeso import generar_barra_progreso
from app.crud import (
    crear_gasto, crear_ingreso, crear_meta, abonar_meta, obtener_meta,
    buscar_meta_por_nombre, eliminar_gasto, eliminar_ingreso, eliminar_meta
)

# Importaciones de routers
from delete_gasto.services.database_models import Gasto as GastoORM, Ingreso as IngresoORM, Meta as MetaORM
from delete_gasto.routers.ayuda import router as ayuda_router
from delete_gasto.routers.metas import router as metas_router
from delete_gasto.routers.reportes import router as reportes_router
from delete_gasto.routers.resumen import router as resumen_router
from delete_gasto.routers.estadistica import router as estadistica_router
from delete_gasto.routers.saldo import router as saldo_router
from delete_gasto.utils.exportaciones import router as exportaciones_router



# Carga de variables y entorno
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TELEGRAM_TOKEN")

if not BOT_TOKEN:
    raise ValueError("No se encontró el Telegram Bot.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# START
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "📊 ¡Bot del tracker financiero activo!\n\n"
        "🎯 ¿Qué puedo hacer por ti hoy?\n\n"
        "📝 <b>Comandos principales:</b>\n"
        "/metas - Ver tus metas\n"
        "/saldo - Ver saldo disponible\n"
        "/comparar_meses - Comparar gastos entre meses\n"
        "/exportar - Exportar reporte financiero\n"
        "/predecir - Predicción de IA\n"
        "/resumen - Ver resumen de gastos\n"
        "/graficos - Ver gráfica de gastos\n"
        "/borrar_gasto [id] - Borrar un gasto\n"
        "/borrar_ingreso [id] - Borrar un ingreso\n"
        "/borrar_meta [nombre] - Borrar una meta\n"
        "/ayuda - Mostrar ayuda\n\n"
        "💬 También puedes escribir natural: 'Me gasté 50 en gasolina'",
        parse_mode="HTML"
    )




# ===== Commands específicos para borrar =====
@dp.message(Command("borrar_gasto"))
async def cmd_borrar_gasto(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Uso: /borrar_gasto [id]")
        return
    busqueda = " ".join(args[1:])
    db = SessionLocal()
    try:
        gasto = db.query(GastoORM).filter(GastoORM.id_gastos == int(busqueda)).first()
        if gasto:
            categoria = gasto.categoria
            monto = gasto.monto
            eliminar_gasto(db, gasto.id_gastos)
            await message.answer(f"✅ Gasto '{categoria}' (${monto:,.0f}) con ID {gasto.id_gastos} eliminado.")
            eliminar_de_sheets("Movimientos", categoria, monto)
        else:
            await message.answer("⚠️ No se encontró el gasto.")
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
    finally:
        db.close()

@dp.message(Command("borrar_ingreso"))
async def cmd_borrar_ingreso(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Uso: /borrar_ingreso [id]")
        return
    busqueda = " ".join(args[1:])
    db = SessionLocal()
    try:
        ingreso = db.query(IngresoORM).filter(IngresoORM.id_ingresos == int(busqueda)).first()
        if ingreso:
            categoria = ingreso.categoria
            monto = ingreso.monto
            eliminar_ingreso(db, ingreso.id_ingresos)
            await message.answer(f"✅ Ingreso '{categoria}' (${monto:,.0f}) con ID {ingreso.id_ingresos} eliminado.")
            eliminar_de_sheets("Movimientos", categoria, monto)
        else:
            await message.answer("⚠️ No se encontró el ingreso.")
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
    finally:
        db.close()

@dp.message(Command("borrar_meta"))
async def cmd_borrar_meta(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Uso: /borrar_meta [nombre]")
        return
    busqueda = " ".join(args[1:])
    db = SessionLocal()
    try:
        meta = buscar_meta_por_nombre(db, busqueda)
        if meta:
            eliminar_meta(db, meta)
            await message.answer(f"✅ Meta '{meta.nombre}' eliminada.")
            eliminar_de_sheets("Movimientos", meta.nombre, meta.monto_objetivo)  # Assuming you want to remove the meta from Movimientos
        else:
            await message.answer("⚠️ No se encontró la meta.")
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
    finally:
        db.close()



@dp.message(lambda msg: msg.text and not msg.text.startswith("/"))
async def registrar_transaccion(message: types.Message):
    if not message.text:
        await message.answer("⚠️ Mándeme texto que con imágenes o stickers no brego todavía.")
        return
    texto = message.text
    # 1. Procesar con Gemini
    datos = procesar_mensaje_financiero(texto)
    
    if not datos or "tipo" not in datos:
        await message.answer("⚠️ Mi hermano, no entendí bien ese movimiento. Intente de nuevo con más detalle.")
        return

    tipo = datos.get("tipo", "").lower()
    
    # Manejar fecha string a date object
    fecha_str = datos.get("fecha")
    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else datetime.now().date()
    except Exception:
        fecha_obj = datetime.now().date()

    db = SessionLocal()
    try:
        if tipo == "gasto":
            gasto_data = GastoSchema(
                id_gastos=None,  # Asumiendo que el ID es autoincremental y se genera automáticamente
                fecha=fecha_obj,
                categoria=datos.get("categoria", "General"),
                monto=float(datos.get("monto", 0.0)),
                descripcion=datos.get("descripcion", texto),
                metodo_pago=datos.get("metodo_pago_o_metodo_ingreso", "Efectivo")
            )
            gasto_guardado = crear_gasto(db, gasto_data)
            # Sincronizar con Google Sheets
            registrar_en_sheets(
                id = gasto_guardado.id_gastos,
                tipo="gasto",
                fecha=gasto_guardado.fecha,
                categoria=gasto_guardado.categoria,
                monto=gasto_guardado.monto,
                descripcion=gasto_guardado.descripcion,
                metodo=gasto_guardado.metodo_pago
            )
            await message.answer(
                f"✅ *Gasto registrado con éxito*\n"
                f"🏷️ Categoría: {gasto_guardado.categoria}\n"
                f"💰 Monto: ${gasto_guardado.monto:,.0f}\n"
                f"📝 Descripción: {gasto_guardado.descripcion}\n"
                f"💳 Método: {gasto_guardado.metodo_pago}",
                parse_mode="Markdown"
            )
            
        elif tipo == "ingreso":
            ingreso_data = IngresoSchema(
                id_ingresos=None,  # Asumiendo que el ID es autoincremental y se genera automáticamente
                fecha=fecha_obj,
                categoria=datos.get("categoria", "General"),
                monto=float(datos.get("monto", 0.0)),
                descripcion=datos.get("descripcion", texto),
                metodo_ingreso=datos.get("metodo_pago_o_metodo_ingreso", "Efectivo")
            )
            ingreso_guardado = crear_ingreso(db, ingreso_data)
            # Sincronizar con Google Sheets
            registrar_en_sheets(
                id = ingreso_guardado.id_ingresos,
                tipo="ingreso",
                fecha=ingreso_guardado.fecha,
                categoria=ingreso_guardado.categoria,
                monto=ingreso_guardado.monto,
                descripcion=ingreso_guardado.descripcion,
                metodo=ingreso_guardado.metodo_ingreso
            )
            await message.answer(
                f"✅ *Ingreso registrado con éxito*\n"
                f"🏷️ Categoría: {ingreso_guardado.categoria}\n"
                f"💰 Monto: ${ingreso_guardado.monto:,.0f}\n"
                f"📝 Descripción: {ingreso_guardado.descripcion}\n"
                f"💳 Método: {ingreso_guardado.metodo_ingreso}",
                parse_mode="Markdown"
            )

        elif tipo == "meta_crear":
            fecha_limite_str = datos.get("fecha_limite")
            try:
                fecha_limite_obj = datetime.strptime(fecha_limite_str, "%Y-%m-%d").date() if fecha_limite_str else datetime.now().date()
            except Exception:
                fecha_limite_obj = datetime.now().date()

            meta_data = MetaSchema(
                nombre=datos.get("nombre", "Meta sin nombre"),
                descripcion=datos.get("descripcion", texto),
                monto_objetivo=float(datos.get("monto_objetivo", 0.0)),
                monto_actual=0.0,
                fecha_limite=fecha_limite_obj
            )
            meta_guardada = crear_meta(db, meta_data)
            # Registrar meta en Google Sheets
            registrar_meta_en_sheets(
                nombre=meta_guardada.nombre,
                objetivo=meta_guardada.monto_objetivo,
                actual=meta_guardada.monto_actual,
                fecha_limite=meta_guardada.fecha_limite,
                descripcion=meta_guardada.descripcion
            )
            await message.answer(
                f"🎯 *¡Nueva meta creada!*\n\n"
                f"📌 Nombre: {meta_guardada.nombre}\n"
                f"🎯 Objetivo: ${meta_guardada.monto_objetivo:,.0f}\n"
                f"📅 Fecha límite: {meta_guardada.fecha_limite}",
                parse_mode="Markdown"
            )

        elif tipo == "meta_abono":
            nombre_meta = datos.get("nombre", "")
            monto_abono = float(datos.get("monto", 0.0))
            meta = buscar_meta_por_nombre(db, nombre_meta)
            
            if not meta:
                await message.answer(f"⚠️ No encontré ninguna meta con el nombre '{nombre_meta}'. Usa /metas para ver las que tienes.")
                return
            meta_actualizada = abonar_meta(db, meta, monto_abono)
            
            # Sincronizar metas con Google Sheets
            sincronizar_todas_las_metas_con_sheets(db)
            
            porcentaje = (meta_actualizada.monto_actual / meta_actualizada.monto_objetivo * 100) if meta_actualizada.monto_objetivo > 0 else 0
            barra = generar_barra_progreso(meta_actualizada.monto_actual, meta_actualizada.monto_objetivo)
            await message.answer(
                f"💰 *¡Abono registrado a tu meta!*\n\n"
                f"📌 Meta: {meta_actualizada.nombre}\n"
                f"➕ Abonado: ${monto_abono:,.0f}\n"
                f"📊 Progreso: ${meta_actualizada.monto_actual:,.0f} / ${meta_actualizada.monto_objetivo:,.0f} ({porcentaje:.1f}%)\n"
                f"[{barra}]",
                parse_mode="Markdown"
            )

        else:
            await message.answer("⚠️ No pude determinar si fue un gasto, ingreso, meta o abono.")
    except Exception as e:
        await message.answer(f"❌ Error guardando en la base de datos: {e}")
    finally:
        db.close()


async def main():
    logging.basicConfig(level=logging.INFO)
    # Define la lista de comandos
    commands = [
        BotCommand(command="start", description="Iniciar el bot"),
        BotCommand(command="metas", description="Ver tus metas"),
        BotCommand(command="resumen", description="Resumen de gastos"),
        BotCommand(command="saldo", description="Ver saldo disponible"),
        BotCommand(command="graficos", description="Ver gráfica de gastos"),
        BotCommand(command="ayuda", description="Ayuda y comandos")
    ]
# Registrar comandos (no crítico, envuelto en try/except)
    try:
        await bot.set_my_commands(commands)
        print("✅ Comandos registrados en Telegram.")
    except Exception as e:
        print(f"⚠️ No se pudieron registrar los comandos: {e}")
        # Continuamos igual, el bot funciona sin el menú de comandos

    # ¡REGISTRAMOS LOS ROUTERS AQUÍ! Esto es CLAVE
    dp.include_router(ayuda_router)
    dp.include_router(metas_router)
    dp.include_router(reportes_router)
    dp.include_router(resumen_router)
    dp.include_router(estadistica_router)
    dp.include_router(exportaciones_router)
    dp.include_router(saldo_router)

    print("🚀 ¡Bot de Telegram con IA y Base de Datos corriendo y a la escucha!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot apagado correctamente.")
