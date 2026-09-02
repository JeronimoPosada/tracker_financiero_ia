import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo para generar imágenes sin GUI
import matplotlib.pyplot as plt
import os
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from aiogram import types, Router
from aiogram.filters import Command
from google import genai
from sqlalchemy import func
from delete_gasto.services.ai_parser import procesar_mensaje_financiero
from delete_gasto.services.database_models import Gasto as GastoORM, Ingreso as IngresoORM
import tempfile
from aiogram.types import FSInputFile
from delete_gasto.services.database import SessionLocal

router = Router()

@router.message(Command("comparar_meses"))
async def cmd_comparar_meses(message: types.Message):
    """
    Muestra una gráfica comparando ingresos y gastos entre este mes y el anterior.
    """
    db = SessionLocal()
    try:
        # Definir meses
        now = datetime.now()
        current_month_start = now.replace(day=1)
        last_month_start = (current_month_start.replace(day=1) - timedelta(days=1)).replace(day=1)

        # Función para sumar por rango de fechas
        def suma_por_tipo_inicio_fin(modelo,inicio,fin):
            result = db.query(func.sum(modelo.monto)).filter(
                modelo.fecha >= inicio,
                modelo.fecha < fin
            ).scalar()
            return float(result) if result else 0.0

        # Totales
        ingresos_actuales = suma_por_tipo_inicio_fin(IngresoORM, current_month_start,
                                                      current_month_start + relativedelta(months=1))
        gastos_actuales = suma_por_tipo_inicio_fin(GastoORM, current_month_start,
                              current_month_start + relativedelta(months=1))
        ingresos_anteriores = suma_por_tipo_inicio_fin(IngresoORM, last_month_start, current_month_start)
        gastos_anteriores = suma_por_tipo_inicio_fin(GastoORM, last_month_start, current_month_start)

        labels = ['Ingreso\nActual', 'Gasto\nActual', 'Ingreso\nAnterior', 'Gasto\nAnterior']
        sizes = [ingresos_actuales, gastos_actuales, ingresos_anteriores, gastos_anteriores]
        colors = ['#4CAF50', '#F44336'] * 2

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        ax.set_title("Comparacion de ingresos y gastos")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            plt.savefig(tmp.name, format="png", dpi=100, bbox_inches='tight')
            tmp_path = tmp.name
        plt.close(fig)

        input_file = FSInputFile(tmp_path)
        await message.answer_photo(input_file, caption="📊 Comparativa mes a mes")
        os.remove(tmp_path)  # Limpia la imagen temporal

    except Exception as e:
        await message.answer(f"❌ Error generando comparativa: {e}")
    finally:
        db.close()

@router.message(Command("predecir"))
async def cmd_predecir(message: types.Message):
    db = SessionLocal()
    try:
        desde = datetime.now() - timedelta(days=90)
        gastos = db.query(GastoORM).filter(GastoORM.fecha >= desde).all()
        ingresos = db.query(IngresoORM).filter(IngresoORM.fecha >= desde).all()

        prompt = "Eres un analista financiero personal.\n"
        prompt += "Ingresos (últimos 90 días):\n"
        for ing in ingresos:
            prompt += f"- ${ing.monto:,.0f} en {ing.categoria} ({ing.fecha})\n"
        prompt += "\nGastos (últimos 90 días):\n"
        for gas in gastos:
            prompt += f"- ${gas.monto:,.0f} en {gas.categoria} ({gas.fecha})\n"
        prompt += "\n¿Cuál será mi saldo neto estimado en 30 días? Sé conciso."
        client = genai.Client(api_key=os.getenv("GEMINI_API"))
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[prompt]
        )

        await message.answer(f"🔮 Predicción IA:\n{response.text.strip()}", parse_mode="HTML")

    except Exception as e:
        await message.answer(f"❌ Error generando predicción: {e}")
    finally:
        db.close()

