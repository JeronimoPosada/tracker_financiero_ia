# 🚀 tracker_financiero_ia
**Controla tus finanzas personales con IA — Automatiza, analiza y alcanza tus metas 💸🤖**

![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![AI](https://img.shields.io/badge/AI-Assisted-4caf50?logo=openai&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Integración-Google%20Sheets-0F9D58?logo=google-sheets&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 💡 Sobre el Proyecto
tracker_financiero_ia es una aplicación de seguimiento de gastos personales y gestión de metas financieras potenciada por Inteligencia Artificial. Su objetivo es transformar datos crudos de gastos en insights accionables y automatizar tareas repetitivas (categorización, limpieza y seguimiento de metas) integrándose directamente con hojas de cálculo para una experiencia fluida y reproducible.

> Nota: Diseñado con mentalidad de Ingeniería de Datos — prioriza pipelines reproducibles, calidad de datos y trazabilidad.

---

## ✨ Características Principales
- ✅ Categorización inteligente de transacciones mediante modelos/heurísticas asistidas por IA.
- 🔄 Sincronización bidireccional con Google Sheets (importa/exporta registros).
- 🧹 Limpieza y normalización de datos con Pandas y NumPy.
- 📊 Análisis y resúmenes automáticos: gasto por categoría, tendencias y alertas de metas.
- 🧭 Seguimiento de metas financieras y proyección de cumplimiento.
- 🛡️ Configuración local y segura de credenciales para servicios externos.
- ♻️ Diseñado para pipelines reproducibles y extensión modular.

---

## 🛠️ Arquitectura y Tecnologías
- Lenguaje: Python
- Librerías clave: Pandas, NumPy, requests, google-api-python-client (o gspread), python-dotenv
- Módulos del repo: ingestión → limpieza → análisis → sincronización (sheets) → reportes
- Integraciones IA: parsers/heurísticas para NLP ligero y reglas automáticas
- Persistencia/exchange: Hojas de cálculo como fuente de verdad y backup

---

## ⚙️ Instalación y Configuración

> Requisitos: Python 3.10+ recomendado, credenciales de Google Sheets si usar sincronización.

1. Clona el repositorio:
```bash
git clone https://github.com/<tu-usuario>/tracker_financiero_ia.git
cd tracker_financiero_ia
```

2. Crea y activa un entorno virtual (Linux/Ubuntu):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instala dependencias:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Configura variables de entorno:
- Copia el ejemplo y ajusta:
```bash
cp .env.example .env
# Edita .env con tus claves: GOOGLE_CREDENTIALS_PATH, OPENAI_API_KEY (si aplica), etc.
```

5. Credenciales de Google Sheets:
- Guarda `credentials.json` en `delete_gasto/credentials.json` o la ruta indicada en `.env`.
- Verifica acceso a la hoja de cálculo.

6. Ejecuta la aplicación:
```bash
# Modo script / análisis rápido
python app/main.py

# Si la repo expone routers o scripts independientes (ej. delete_gasto/routers)
python delete_gasto/main.py
```

---

## 📂 Estructura del Proyecto
```
tracker_financiero_ia/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ app/
│  ├─ __init__.py
	│  ├─ main.py
	│  ├─ crud.py
├─ delete_gasto/
│  ├─ credentials.json
│  ├─ routers/
│  │  ├─ analisis.py
│  │  ├─ ayuda.py
│  │  ├─ estadistica.py
│  │  ├─ metas.py
│  │  ├─ reportes.py
│  │  ├─ resumen.py
│  │  └─ saldo.py
│  └─ services/
│     ├─ ai_parser.py
│     ├─ database_models.py
│     ├─ database.py
│     └─ sheets_service.py
├─ utils/
│  ├─ barra_progeso.py
│  ├─ exportaciones.py
│  └─ models.py
```

---

## 🚀 Uso
1. Añade o importa tus transacciones a la hoja de cálculo configurada.
2. Ejecuta el script principal para procesar y categorizar:
```bash
python app/main.py
```
3. Revisa los reportes generados y dashboards exportados a Google Sheets y/o CSV.
4. Ajusta reglas de categorización en `delete_gasto/services/ai_parser.py` para mejorar precisión.


---

## 🗺️ Roadmap
- v0.2 — Integración con un panel web ligero (Streamlit/Flask) para visualización interactiva.
- v0.3 — Modelos de clasificación semi-supervisada para mejorar categorización con feedback del usuario.
- v0.4 — Módulo de recomendaciones (ahorro automático, optimización de metas).
- v0.5 — Conector a múltiples fuentes (bancos CSV, APIs financieras) + pruebas automatizadas y CI.

---

## 🤝 Contribución y Contacto
- ¿Quieres contribuir? ¡Genial! Abre un Issue antes de PR para discutir cambios importantes.
- Buenas prácticas para PRs:
	- Fork → rama feature/xyz → PR con una descripción clara.
	- Incluye tests o ejemplos reproducibles cuando agregues lógica de datos.
- Contacto: abre un Issue o contacta a `jp.posada6@gmail.com`.

---

Gracias por revisar tracker_financiero_ia — una forma más inteligente, reproducible y eficiente de gestionar tus finanzas personales con la ayuda de IA.

