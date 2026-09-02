import os

import matplotlib
matplotlib.use('Agg')  # Backend no interactivo
import matplotlib.pyplot as plt
import io as io_module
from sqlalchemy import func
import io
from aiogram import Router, types
from aiogram.filters import Command
from delete_gasto.services.database import SessionLocal
from delete_gasto.services.database_models import Gasto as GastoORM, Ingreso as IngresoORM, Meta as MetaORM
from aiogram.types import FSInputFile

router = Router()


@router.message(Command("graficos"))
async def cmd_graficos(message: types.Message):
    """
    Genera una imagen con la distribución de gastos y la envía por Telegram.
    """
    db = SessionLocal()
    try:
        total_gastos = db.query(func.sum(GastoORM.monto)).scalar() or 0
        total_ingresos = db.query(func.sum(IngresoORM.monto)).scalar() or 0

        conteo_gastos = db.query(GastoORM).count()
        conteo_ingresos = db.query(IngresoORM).count()

        if total_gastos == 0 and total_ingresos == 0:
            await message.answer("📊 Aún no tienes movimientos registrados para graficar.")
            return

        float_ingresos = float(total_ingresos)
        float_gastos = float(total_gastos)

        label_ingresos = 'Ingresos ($' + format(float_ingresos, ",.0f") + ')\nCantidad: ' + str(conteo_ingresos)
        label_gastos = 'Gastos ($' + format(float_gastos, ",.0f") + ')\nCantidad: ' + str(conteo_gastos)
        labels = [label_ingresos, label_gastos]

        sizes = [float_ingresos, float_gastos]
        colors = ['#4CAF50', '#F44336']
        explode = (0.05, 0)

        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(
            sizes,
            explode=explode,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',  
            shadow=True,
            startangle=90,
            pctdistance=0.85
        )

        ax1.set_title("💰 Control de Ingresos vs. Gastos 💰", fontsize=14, fontweight='bold')

        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig1.gca().add_artist(centre_circle)

        # ✅ Guardar en disco en lugar de BytesIO
        ruta_temp = "/tmp/grafico_temp.png"
        plt.savefig(ruta_temp, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig1)

        input_file = FSInputFile(ruta_temp, filename="control_financiero.png")
        await message.answer_photo(input_file, caption="📊 Distribución de tus ingresos y gastos.")

        # Limpiar archivo temporal después de enviar
        os.remove(ruta_temp)

    except Exception as e:
        print(f"❌ ERROR DETALLADO: {type(e).name}: {e}") 
        await message.answer(f"❌ Error generando gráfico: {e}")
    finally:
        db.close()





    