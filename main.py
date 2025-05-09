import json
import os
import streamlit as st
import pandas as pd
from scraper.listado import obtener_listado_particulares
from scraper.detalles import obtener_detalles, crear_driver_detalles

def generar_slug(texto):
    import unidecode
    return (
        unidecode.unidecode(texto.lower())
        .replace("/", "-")
        .replace(",", "")
        .replace(".", "")
        .replace(" ", "-")
    )

# ========= Cargar JSONs ==========
BASE_PATH = os.path.join("localidades", "CPPP")

with open(os.path.join(BASE_PATH, "ccaa.json"), encoding="utf-8") as f:
    ccaa = json.load(f)

with open(os.path.join(BASE_PATH, "provincias.json"), encoding="utf-8") as f:
    provincias = json.load(f)

with open(os.path.join(BASE_PATH, "poblaciones.json"), encoding="utf-8") as f:
    poblaciones = json.load(f)

# ========= UI Streamlit ==========
st.title("Scraper Inmobiliario - Particulares Idealista")

ccaa_opciones = [c["label"] for c in ccaa]
ccaa_sel = st.selectbox("Selecciona Comunidad Autónoma", ccaa_opciones)

codigo_ccaa = next(c["code"] for c in ccaa if c["label"] == ccaa_sel)
provincias_filtradas = [p for p in provincias if p["parent_code"] == codigo_ccaa]
prov_opciones = [p["label"] for p in provincias_filtradas]
prov_sel = st.selectbox("Selecciona Provincia", prov_opciones)

codigo_prov = next(p["code"] for p in provincias if p["label"] == prov_sel)
poblaciones_filtradas = [m for m in poblaciones if m["parent_code"] == codigo_prov]
pob_opciones = [m["label"] for m in poblaciones_filtradas]
pob_sel = st.selectbox("Selecciona Población", pob_opciones)

slug = generar_slug(f"{pob_sel} {prov_sel}")

# ========= Scraping ==========
if st.button("Buscar propiedades") and slug:
    try:
        with st.spinner("Buscando listados de viviendas..."):
            df_listado = obtener_listado_particulares(slug)

        if df_listado.empty:
            st.warning("No se encontraron propiedades en esta zona.")
        else:
            st.success(f"{len(df_listado)} propiedades encontradas en el listado inicial.")
            st.write(df_listado)

            detalles_completos = []
            progreso = st.progress(0)
            errores = 0

            driver = crear_driver_detalles()

            # Aquí ya no necesitamos comprobar si es particular, porque ya lo hace detalles.py
            for idx, (_, row) in enumerate(df_listado.iterrows()):
                try:
                    detalle = obtener_detalles(driver, row['url'])
                    # Añadimos todos los detalles (los cuales ya han sido filtrados como particulares)
                    if detalle:
                        detalles_completos.append(detalle)
                    else:
                        st.warning(f"Anuncio no es particular o error al procesar: {row['url']}")
                except Exception as e:
                    st.error(f"Error procesando {row['url']}: {e}")
                    errores += 1

                progreso.progress((idx + 1) / len(df_listado))  # Actualizamos el progreso de la barra

            driver.quit()

            # Verificamos si detalles_completos está vacío correctamente
            if not detalles_completos:
                st.warning("No se encontraron particulares en esta búsqueda.")
            else:
                df_detalles = pd.DataFrame(detalles_completos)
                st.success(f"Se encontraron {len(df_detalles)} particulares.")
                st.dataframe(df_detalles)

                os.makedirs("data", exist_ok=True)
                csv_path = os.path.join("data", f"leads_particulares_{slug}.csv")
                df_detalles.to_csv(csv_path, index=False, encoding="utf-8")

                csv = df_detalles.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar resultados en CSV",
                    data=csv,
                    file_name=f"leads_particulares_{slug}.csv",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"🚨 Error inesperado durante el scraping: {e}")
