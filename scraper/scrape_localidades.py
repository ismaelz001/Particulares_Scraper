from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import sys

def obtener_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_zonas_por_ciudad(slug_ciudad):
    url = f"https://www.idealista.com/venta-viviendas/{slug_ciudad}/"

    driver = obtener_driver()
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    zonas = []
    filtros = soup.find_all("li", class_="filter-multiselect-checkbox")

    for filtro in filtros:
        span = filtro.find("span", class_="filter-multiselect-checkbox-text")
        if span:
            texto = span.get_text(strip=True)
            slug = texto.lower().replace(" ", "-").replace("'", "").replace("á", "a").replace("é", "e") \
                .replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
            zonas.append({
                "zona": texto,
                "slug": slug
            })

    output_file = f"zonas_{slug_ciudad}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(zonas, f, ensure_ascii=False, indent=2)

    print(f"✅ Zonas extraídas para '{slug_ciudad}' guardadas en {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Por favor, proporciona el slug de una ciudad. Ej: madrid, valencia, almeria")
    else:
        scrape_zonas_por_ciudad(sys.argv[1])
