import os
import gspread
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")


def get_client():
    return gspread.service_account(filename=CREDENTIALS_FILE)


def get_spreadsheet():
    gc = get_client()
    try:
        sh = gc.open("tracker_financiero")
    except gspread.SpreadsheetNotFound:
        sh = gc.create("tracker_financiero")
        print("📁 Nueva hoja de cálculo 'tracker_financiero' creada.")
    return sh


def registrar_en_sheets(id: int, tipo: str, fecha, categoria: str, monto: float, descripcion: str, metodo: str):
    """
    Registra un gasto o ingreso en la hoja de Google Sheets.
    """
    try:
        sh = get_spreadsheet()
        try:
            wks = sh.worksheet("Movimientos")
        except gspread.WorksheetNotFound:
            wks = sh.add_worksheet(title="Movimientos", rows=1000, cols=20)
            wks.append_row(["ID","Fecha", "Tipo", "Categoría", "Monto", "Descripción", "Método"])

        fila = [int(id), str(fecha), tipo.capitalize(), categoria, float(monto), descripcion, metodo]
        wks.append_row(fila)
        print("📊 Datos registrados en Google Sheets con éxito!")
        
        # Asegurar gráfico nativo en Google Sheets
        asegurar_graficos_en_sheets(sh)
        return sh
    except Exception as e:
        print(f"❌ Error sincronizando con Google Sheets: {e}")
        return None


def registrar_meta_en_sheets(nombre: str, objetivo: float, actual: float, fecha_limite, descripcion: str = ""):
    """
    Registra o actualiza una meta en la pestaña 'Metas' de Google Sheets.
    """
    try:
        sh = get_spreadsheet()
        try:
            wks = sh.worksheet("Metas")
        except gspread.WorksheetNotFound:
            wks = sh.add_worksheet(title="Metas", rows=100, cols=20)
            wks.append_row(["Nombre", "Monto Objetivo", "Monto Actual", "Fecha Límite", "Descripción"])

        fila = [str(nombre), float(objetivo), float(actual), str(fecha_limite), descripcion]
        wks.append_row(fila)
        print(f"🎯 Meta '{nombre}' registrada en Google Sheets con éxito!")
        
        asegurar_graficos_en_sheets(sh)
        return sh
    except Exception as e:
        print(f"❌ Error registrando meta en Google Sheets: {e}")
        return None


def sincronizar_todas_las_metas_con_sheets(db):
    """
    Limpia y resincroniza todas las metas activas de la DB con Google Sheets.
    """
    try:
        from delete_gasto.services.database_models import Meta
        metas = db.query(Meta).all()
        sh = get_spreadsheet()
        try:
            wks = sh.worksheet("Metas")
            wks.clear()
        except gspread.WorksheetNotFound:
            wks = sh.add_worksheet(title="Metas", rows=100, cols=20)

        wks.append_row(["Nombre", "Monto Objetivo", "Monto Actual", "Fecha Límite", "Descripción"])
        for m in metas:
            wks.append_row([m.nombre, float(m.monto_objetivo), float(m.monto_actual), str(m.fecha_limite), m.descripcion or ""])
        print("🎯 Metas resincronizadas con Google Sheets.")
        
        asegurar_graficos_en_sheets(sh)
        return True
    except Exception as e:
        print(f"❌ Error sincronizando metas con Google Sheets: {e}")
        return False


def eliminar_de_sheets(hoja_nombre: str, categoria: str, monto: float):
    """
    Busca y elimina filas en Google Sheets que coincidan con categoria y monto.
    Nueva estructura de columnas: [ID, Fecha, Tipo, Categoría, Monto, Descripción, Método]
    """
    try:
        sh = get_spreadsheet()
        wks = sh.worksheet(hoja_nombre)
        rows = wks.get_all_values()
        
        categoria_buscada = categoria.strip().lower()
        monto_buscado = str(float(monto))  # Aseguramos el mismo formato numérico
        
        print(f"🔍 Buscando en Sheets: categoría='{categoria_buscada}', monto='{monto_buscado}'")
        print(f"📋 Estructura de la hoja: {rows[0] if rows else 'vacía'}")
        
        for i in range(len(rows) - 1, 0, -1):  # Empezamos desde el fondo para no romper índices
            row = rows[i]
            if len(row) >= 5:
                categoria_fila = row[3].strip().lower()  # Posición 3 = Categoría
                monto_fila = str(float(row[4])).strip()   # Posición 4 = Monto
                
                print(f"   Fila {i+1}: Categoría='{categoria_fila}' vs '{categoria_buscada}' | Monto='{monto_fila}' vs '{monto_buscado}'")
                
                if categoria_fila == categoria_buscada and monto_fila == monto_buscado:
                    print(f"✅ COINCIDENCIA ENCONTRADA EN LA FILA {i + 1}. Borrando...")
                    wks.delete_rows(i + 1)  # +1 porque get_all_values indexa desde 0, pero Sheets desde 1
                    return True
        print("❌ No se encontró ninguna coincidencia.")
        return False
        
    except gspread.exceptions.APIError as e:
        print(f"❌ Error de API de Google Sheets: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general al borrar en Sheets: {e}")
        return False






def asegurar_graficos_en_sheets(sh=None):
    """
    Crea o actualiza gráficos nativos directamente en la hoja de Google Sheets.
    """
    try:
        if not sh:
            sh = get_spreadsheet()

        try:
            wks_mov = sh.worksheet("Movimientos")
            sheet_id = wks_mov.id

            req = {
                "requests": [
                    {
                        "addChart": {
                            "chart": {
                                "spec": {
                                    "title": "Gastos e Ingresos por Categoría",
                                    "basicChart": {
                                        "chartType": "COLUMN",
                                        "legendPosition": "BOTTOM_LEGEND",
                                        "axis": [
                                            {"position": "BOTTOM_AXIS", "title": "Categorías"},
                                            {"position": "LEFT_AXIS", "title": "Monto ($)"}
                                        ],
                                        "domains": [
                                            {
                                                "domain": {
                                                    "sourceRange": {
                                                        "sources": [
                                                            {
                                                                "sheetId": sheet_id,
                                                                "startRowIndex": 0,
                                                                "startColumnIndex": 2,  # Col C (Categoría)
                                                                "endColumnIndex": 3
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        ],
                                        "series": [
                                            {
                                                "series": {
                                                    "sourceRange": {
                                                        "sources": [
                                                            {
                                                                "sheetId": sheet_id,
                                                                "startRowIndex": 0,
                                                                "startColumnIndex": 3,  # Col D (Monto)
                                                                "endColumnIndex": 4
                                                            }
                                                        ]
                                                    }
                                                },
                                                "targetAxis": "LEFT_AXIS"
                                            }
                                        ],
                                        "headerCount": 1
                                    }
                                },
                                "position": {
                                    "overlayPosition": {
                                        "anchorCell": {
                                            "sheetId": sheet_id,
                                            "rowIndex": 1,
                                            "columnIndex": 7  # Col H
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }
            sh.batch_update(req)
            print("📈 Gráfico generado en Google Sheets.")
        except Exception as e:
            # Si el gráfico ya existe o hay conflicto de rango, continuamos sin fallar
            pass
    except Exception as e:
        print(f"Info grafico sheets: {e}")
