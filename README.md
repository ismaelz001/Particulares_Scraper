# 🏠 Particulares Scraper - Idealista (Streamlit App)

Aplicación desarrollada en Streamlit para scrapear datos de contacto (nombre y teléfono) de personas que publican viviendas **como particulares** en Idealista. Pensada para generar **leads inmobiliarios** útiles para agentes y comerciales que desean contactar directamente con propietarios.

---

## 📌 Características principales

- Aplicación web interactiva con Streamlit.
- Permite seleccionar zonas/localidades a scrapear.
- Extrae datos de nombre, teléfono, URL y localidad.
- Exporta los leads a archivos `.csv` organizados.
- Configuración modular por provincias/localidades.

---

## 🖥️ Vista de la App

La aplicación se ejecuta en local como una interfaz web donde puedes:

- Cargar la configuración de zonas
- Iniciar el proceso de scraping
- Ver los leads obtenidos en pantalla
- Descargar los datos en CSV

---

## 📂 Estructura del proyecto
particulares_scraper/
├── main.py # Script principal de Streamlit
├── requirements.txt # Dependencias necesarias
├── .gitignore # Archivos excluidos del repo
├── README.md # Este archivo
├── data/ # CSVs generados con leads
│ └── leads_particulares_<zona>.csv
├── localidades/ # Configuración por localidad
│ └── CPPP/ # Subcarpeta con archivos de zonas




Pega esto directamente en tu archivo `README.md` y haz el push:

```bash
git add README.md
git commit -m "READMEpara versión Streamlit del scraper"
git push
