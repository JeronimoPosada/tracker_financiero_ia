import os
import json
from datetime import date
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API")
client = genai.Client(api_key=api_key)

def obtener_system_prompt() -> str:
    hoy = date.today().strftime("%Y-%m-%d")
    ano_actual = str(date.today().year)

    parts = []

    parts.append("Eres el motor de IA de un tracker financiero personal en Colombia. ")
    parts.append("Tu trabajo es analizar mensajes en lenguaje natural y extraer la información en un formato JSON estricto.")

    parts.append("")
    parts.append("⚠️ INFORMACIÓN TEMPORAL OBLIGATORIA:")
    parts.append("- La fecha actual de HOY es: " + hoy + " (Año " + ano_actual + ").")
    parts.append("- Cualquier cálculo de fecha relativa (\"en diciembre\", \"el próximo mes\", \"en 6 meses\", \"ayer\", etc.) DEBE calcularse a partir de " + hoy + ".")

    parts.append("")
    parts.append("Debes clasificar el tipo de movimiento en una de estas opciones en el campo \"tipo\":")
    parts.append("1. \"gasto\": Para salidas de dinero (ej: \"Gasté 20 lucas en cine\").")
    parts.append("2. \"ingreso\": Para entradas de dinero (ej: \"Me pagaron 1 millón de nómina\").")
    parts.append("3. \"meta_crear\": Cuando el usuario quiere crear un nuevo objetivo o meta de ahorro (ej: \"Quiero ahorrar 800 mil pal celular antes de diciembre\").")
    parts.append("4. \"meta_abono\": Cuando el usuario abona o mete plata a una meta existente (ej: \"Le metí 50 lucas a la meta del celular\").")

    parts.append("")
    parts.append("Estructura del JSON que DEBES devolver según el tipo:")

    parts.append("")
    parts.append("Si es \"gasto\" o \"ingreso\":")
    parts.append('{')
    parts.append('    "tipo": "gasto" o "ingreso",')
    parts.append('    "fecha": "' + hoy + '",')
    parts.append('    "categoria": "Ej: Comida, Transporte, Salario, Ocio, etc.",')
    parts.append('    "monto": float (ej: 25 lucas = 25000),')
    parts.append('    "descripcion": "Breve descripción",')
    parts.append('    "metodo_pago_o_metodo_ingreso": "Efectivo, Tarjeta, Transferencia, Nequi, Daviplata. (Si no se especifica, usa Efectivo)"')
    parts.append('}')

    parts.append("")
    parts.append("Si es \"meta_crear\":")
    parts.append('{')
    parts.append('    "tipo": "meta_crear",')
    parts.append('    "nombre": "Nombre corto de la meta (ej: Celular, Viaje a Cartagena, Carro)",')
    parts.append('    "descripcion": "Descripción detallada del objetivo",')
    parts.append('    "monto_objetivo": float,')
    parts.append('    "fecha_limite": "YYYY-MM-DD" (calcula la fecha límite a partir de ' + hoy + '. Si dice \"en diciembre\", usa ' + ano_actual + '-12-31)')
    parts.append('}')

    parts.append("")
    parts.append("Si es \"meta_abono\":")
    parts.append('{')
    parts.append('    "tipo": "meta_abono",')
    parts.append('    "nombre": "Nombre de la meta a la que le va a abonar",')
    parts.append('    "monto": float')
    parts.append('}')

    return "\n".join(parts)


MODELOS_DISPONIBLES = [
    "gemini-3.5-flash-lite",        # Principal (Rápido y muy estable)
    "gemini-3.5-flash",
    "gemini-3.6-flash"           # Respaldo
]

def procesar_mensaje_financiero(texto: str) -> dict:
    """Procesa un mensaje financiero usando la interfaz Chat para evitar error 404."""
    prompt_actualizado = obtener_system_prompt()
    # Intentar cada modelo disponible hasta que uno funcione
    for modelo in MODELOS_DISPONIBLES:
        try:
            chat = client.chats.create(model=modelo)
            response = chat.send_message(texto,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_actualizado,
                    response_mime_type="application/json",
                )
            )
            try:
                datos = json.loads(response.text or "{}")
            except Exception as parse_err:
                print(f"⚠️ Error parseando respuesta del modelo {modelo}: {parse_err}")
                continue

            if isinstance(datos, dict) and datos:
                return datos
            else:
                print(f"⚠️ Modelo {modelo} devolvió JSON vacío o no válido: {response.text}")
        except Exception as e:
            print(f"⚠️ Error procesando con modelo {modelo}: {e}")
            # seguir con el siguiente modelo
            continue

    # Si ningún modelo funcionó
    return None

def obtener_respuesta_chat(texto: str, modelo: str = None) -> dict:
    """Versión alternativa usando la interfaz Chat."""
    # Construir la lista de modelos a probar: si se especifica uno, probarlo primero
    modelos_a_probar = []
    if modelo:
        modelos_a_probar.append(modelo)
    for m in MODELOS_DISPONIBLES:
        if m not in modelos_a_probar:
            modelos_a_probar.append(m)

    for m in modelos_a_probar:
        try:
            chat = client.chats.create(model=m)
            response = chat.send_message(texto,
                config=types.GenerateContentConfig(
                    system_instruction=obtener_system_prompt(),
                    response_mime_type="application/json",
                )
            )
            try:
                datos = json.loads(response.text or "{}")
            except Exception as parse_err:
                print(f"⚠️ Error parseando respuesta del modelo {m}: {parse_err}")
                continue

            if isinstance(datos, dict) and datos:
                return datos
            else:
                print(f"⚠️ Modelo {m} devolvió JSON vacío o no válido: {response.text}")
        except Exception as e:
            print(f"⚠️ Error con modelo {m} usando Chat: {e}")
            continue

    return None