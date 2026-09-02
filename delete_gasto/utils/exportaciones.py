import os
import tempfile
from fpdf import FPDF
from aiogram import types, Router
from aiogram.filters import Command
from delete_gasto.services.database_models import Gasto as GastoORM, Ingreso as IngresoORM

from delete_gasto.services.database import SessionLocal


router = Router()

def clean_txt(t):
    if not t:
        return ""
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
    }
    cleaned = str(t)
    for k, v in replacements.items():
        cleaned = cleaned.replace(k, v)
    return cleaned.encode('latin-1', 'ignore').decode('latin-1')

@router.message(Command("exportar"))
async def cmd_exportar(message: types.Message):
    """
    Exporta tu historial financiero completo a un PDF
    """

    db = SessionLocal()
    try: 
        gastos = db.query(GastoORM).all()
        ingresos = db.query(IngresoORM).all()

        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Reporte Financiero Personal", ln=True, align='C')
        pdf.ln(10)

        pdf.cell(200, 10, "Gastos:", ln=True)
        for g in gastos:
            txt_gasto = f"{g.fecha} - {clean_txt(g.categoria)} - ${g.monto:,.0f}"
            pdf.cell(200, 8, txt_gasto, ln=True)
        pdf.ln(5)

        pdf.cell(200, 10, "Ingresos:", ln=True)
        for i in ingresos:
            txt_ingreso = f"{i.fecha} - {clean_txt(i.categoria)} - ${i.monto:,.0f}"
            pdf.cell(200, 8, txt_ingreso, ln=True)

        # Guardar en Temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            path_pdf = tmp_file.name

        # Enviar PDF
        input_file = types.FSInputFile(path_pdf, filename="reporte_financiero.pdf")
        await message.answer_document(input_file, caption="Aqui esta tu reporte financiero completo.")

        os.remove(path_pdf)  # Limpiar archivo temporal
    except Exception as e:
        await message.answer(f"❌ Error generando reporte: {e}")
    finally:
        db.close()
