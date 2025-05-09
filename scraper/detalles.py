from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random

def crear_driver_detalles():
    opciones = Options()
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-gpu')
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option('useAutomationExtension', False)
    opciones.add_argument('--window-size=1280,800')
    opciones.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)
    return driver

def detectar_captcha(soup):
    if soup.select_one('div#captcha'):
        return True
    if soup.find('h1') and 'error' in soup.find('h1').text.lower():
        return True
    return False

def obtener_detalles(driver, url):
    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8))

        # 🔥 Scroll para asegurar carga completa
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))

        # 🔥 Aceptar cookies si aparecen
        try:
            aceptar_cookies = driver.find_element(By.ID, "didomi-notice-agree-button")
            if aceptar_cookies.is_displayed():
                aceptar_cookies.click()
                print("✅ Cookies aceptadas")
                time.sleep(2)
        except NoSuchElementException:
            print("ℹ️ No había cookies para aceptar.")
        except Exception as e:
            print(f"⚠️ Error aceptando cookies: {e}")

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        if detectar_captcha(soup):
            print(f"🚨 CAPTCHA detectado en {url}, saltando anuncio.")
            return None

        texto_completo = soup.get_text().lower()

        # 🔥 Filtrar solo anuncios de particulares
        if "particular" not in texto_completo:
            print(f"⛔ No es particular en {url}, ignorando anuncio.")
            return None

        resultado = {
            "nombre": "No disponible",
            "telefono": "No disponible",
            "url": url
        }

        # 🔥 Intentamos ocultar el botón de "Guardar favorito" que bloquea el click
        try:
            favorito_button = driver.find_element(By.CSS_SELECTOR, 'button.favorite-btn')
            if favorito_button.is_displayed():
                driver.execute_script("arguments[0].style.display = 'none';", favorito_button)
                print("✅ Se ha ocultado el botón 'Guardar favorito'")
                time.sleep(2)
        except Exception as e:
            print(f"⚠️ No se pudo ocultar el bloqueador 'Guardar favorito': {e}")

        # 🔥 Intentamos ocultar el sticky-bar que bloquea después
        try:
            sticky_bar = driver.find_element(By.CSS_SELECTOR, 'p.sticky-bar-detail-heading.txt-body')
            if sticky_bar.is_displayed():
                driver.execute_script("arguments[0].style.display = 'none';", sticky_bar)
                print("✅ Se ha ocultado el sticky-bar")
                time.sleep(2)
        except Exception as e:
            print(f"⚠️ No se pudo ocultar el sticky-bar: {e}")

        # 🔥 Desplazar la página hasta el botón "Ver teléfono"
        try:
            ver_telefono_link = driver.find_element(By.CSS_SELECTOR, 'a.hidden-contact-phones_link')
            driver.execute_script("arguments[0].scrollIntoView(true);", ver_telefono_link)  # Desplazamos a él
            time.sleep(1)

            # 🔥 Intentar click normal
            if ver_telefono_link.is_displayed() and ver_telefono_link.is_enabled():
                ver_telefono_link.click()
                print(f"✅ Click en 'Ver teléfono' en {url}")
                time.sleep(6)  # Espera más larga para asegurar que el número cargue

        except Exception as e:
            print(f"⚠️ No se pudo clicar 'Ver teléfono' de forma normal: {e}")

            # 🔥 Intentar click con JavaScript si el normal falla
            try:
                driver.execute_script("arguments[0].click();", ver_telefono_link)  # Forzamos el click con JS
                print(f"✅ Click forzado en 'Ver teléfono' en {url}")
                time.sleep(6)  # Espera más larga para asegurar que el número cargue
            except Exception as js_error:
                print(f"⚠️ No se pudo hacer click forzado en 'Ver teléfono': {js_error}")

        # 🔥 Refrescamos el DOM después del click
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 🔥 Buscar el teléfono en el span
        telefono_span = soup.find('a', class_='icon-phone-outline hidden-contact-phones_formatted-phone _mobilePhone')
        if telefono_span:
            texto_span = telefono_span.find('span', class_='hidden-contact-phones_text').get_text().strip()
            if texto_span:
                resultado["telefono"] = texto_span
                print(f"✅ Teléfono extraído del span: {texto_span}")
            else:
                resultado["telefono"] = "No disponible"
        else:
            resultado["telefono"] = "No disponible"

        # 🔥 Buscar nombre del anunciante
        # Corregimos la manera de buscar el nombre
        nombre_tag = soup.find("span", class_="particular")
        if nombre_tag:
            resultado["nombre"] = nombre_tag.find_next("input").get("value").strip()  # Obtener valor de 'user-name'

        return resultado

    except Exception as e:
        print(f"⚠️ Error extrayendo detalles de {url}: {e}")
        return None
