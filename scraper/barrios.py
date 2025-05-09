from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import unidecode

def obtener_driver():
    opciones = Options()
    opciones.add_argument('--headless')
    opciones.add_argument('--disable-gpu')
    opciones.add_argument('--no-sandbox')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)

def generar_slug(texto):
    return unidecode.unidecode(texto.lower().replace(" ", "-"))

def obtener_barrios(ciudad, distrito=None):  # El distrito no se usa para formar la URL
    slug_ciudad = generar_slug(ciudad)
    partes_url = [slug_ciudad]

    url = f"https://www.idealista.com/venta-viviendas/{'/'.join(partes_url)}/"

    driver = obtener_driver()
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    barrios = []
    filtros_barrios = soup.find_all("li", class_="filter-multiselect-checkbox")

    for filtro in filtros_barrios:
        span = filtro.find("span", class_="filter-multiselect-checkbox-text")
        if span:
            barrios.append(span.text.strip())

    return barrios
