from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
import os

def obtener_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--window-size=1280,800')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    return driver

def detectar_captcha(soup):
    return bool(soup.select_one('div#captcha'))

def obtener_listado_particulares(slug, max_paginas=None, guardar_html_debug=False):
    url_base = f"https://www.idealista.com/venta-viviendas/{slug}/"
    driver = obtener_driver()
    resultados = []
    urls_vistas = set()
    pagina = 1

    try:
        while True:
            url = url_base if pagina == 1 else f"{url_base}pagina-{pagina}.htm"
            print(f"🌀 Cargando página {pagina}: {url}")

            try:
                driver.get(url)
                time.sleep(random.uniform(3, 7))
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"⚠️ Error cargando página {pagina}: {e}")
                break

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            if detectar_captcha(soup):
                print("🚨 CAPTCHA detectado, deteniendo scraping.")
                break

            viviendas = soup.select('article.item')
            print(f"🔍 Encontrados {len(viviendas)} artículos en esta página")

            if guardar_html_debug:
                os.makedirs("debug_pages", exist_ok=True)
                with open(f"debug_pages/pagina_debug_{pagina}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)

            if not viviendas:
                print("🔚 No hay viviendas, fin del scraping.")
                break

            nuevas_urls = set()

            for vivienda in viviendas:
                titulo_tag = vivienda.find('a', class_='item-link')
                precio_tag = vivienda.find('span', class_='item-price')

                titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"
                precio = precio_tag.text.strip() if precio_tag else "Sin precio"
                url_vivienda = "https://www.idealista.com" + titulo_tag['href'] if titulo_tag else ""

                if url_vivienda in urls_vistas:
                    continue  # Ya la hemos visto
                nuevas_urls.add(url_vivienda)

                resultados.append({
                    "titulo": titulo,
                    "precio": precio,
                    "url": url_vivienda
                })

            if len(nuevas_urls) == 0:
                print("🛑 No se encontraron URLs nuevas, Idealista está repitiendo la página. Fin del scraping.")
                break

            urls_vistas.update(nuevas_urls)
            pagina += 1

            if max_paginas and pagina > max_paginas:
                print(f"⏹️ Alcanzado límite de {max_paginas} páginas, deteniendo.")
                break

    finally:
        driver.quit()

    print(f"✅ Total propiedades encontradas: {len(resultados)}")
    return pd.DataFrame(resultados)
