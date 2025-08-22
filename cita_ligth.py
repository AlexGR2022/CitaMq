import time
import winsound
import os

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BRAVE_PATH = r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"

chromedriver_path = "C:\\WebDrivers\\chromedriver.exe"
URL_FILE = "url.txt"
DEFAULT_URL = "https://citaprevia.ciencia.gob.es/qmaticwebbooking/#/"
OPCION_XPATH = "//input[@type='radio' and @aria-label='Asistencia telefónica para la homologación y equivalencia de títulos universitarios extranjeros']"
FECHA_XPATH = "//button[@id='dateTimePanel' and .//div[contains(text(),'Seleccionar fecha y hora')]]"
HORA_BTN_XPATH = "//span[contains(@class,'v-btn__content') and contains(text(),':')]"



#############################################################################################

segundos_antes= 3                            # segundos antes de la hora en punto para comenzar a intentar. 
duracion_intento = 4                         # Duración del intento en segundos
hora_de_inicio = "8:49:00"                   # Hora en que la url comienza a tirar los turnos (10:00 madrid,9:00 canarias)
hora_de_final = "22:00:00"                   # Hora de finalización (14:00 madrid, 13:00 canarias) y cierre de la app.

##############################################################################################
"""
def mostrar_mensaje(driver, mensaje):
    driver.execute_script('''
        if (!window._msgBox) {
            var box = document.createElement('div');
            box.id = '_msgBox';
            box.style.position = 'fixed';
            box.style.top = '20px';
            box.style.left = '50%';
            box.style.transform = 'translateX(-50%)';
            box.style.background = 'rgba(0,0,0,0.8)';
            box.style.color = 'white';
            box.style.padding = '10px 20px';
            box.style.zIndex = 9999;
            box.style.fontSize = '18px';
            box.style.borderRadius = '8px';
            box.style.maxWidth = '80vw';
            box.style.textAlign = 'center';
            document.body.appendChild(box);
            window._msgBox = box;
            window._msgBox._lastText = '';
        }
        if (window._msgBox._lastText !== arguments[0]) {
            window._msgBox.innerText = arguments[0];
            window._msgBox._lastText = arguments[0];
        }
    ''', mensaje)
    """

def alarma():
    winsound.Beep(1000, 1000)  # Sonido de alarma


def esperar_hora(segundos_antes):
    """
    Las horas aparecen a la hora en punto y luego cada 10 minutos, osea a las y 10,20,30,40,50 y 00._________________________________________________
    """

    # Espera hasta el minuto 9,19,29,39,49 o 59. Luego añade (60 - segundos_antes) para comenzar:
    while True:
        ahora = datetime.now()
        if ahora.minute % 10 == 9:              # poner el minuto antes
            break
        time.sleep(1)

    time.sleep(60 - segundos_antes)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] tiempo antes alcanzado ok... ...")

    return True



def ejecutar_intentos(driver):    # ejecuta ciclo de intentos de duracion x, luego retorna a main()

    fin = datetime.now() + timedelta(seconds= duracion_intento) 
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] ejecutando intentos: ...")
    while datetime.now() < fin:
        try:
            #driver.execute_script("document.body.style.zoom='80%'")    # Establecer zoom

            # Intentar forzar el click con JavaScript si el elemento existe:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Buscando opción de asistencia telefónica...")
                radio_js = driver.find_element(By.XPATH, OPCION_XPATH)
                print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Haciendo click sobre la opción")
                driver.execute_script("arguments[0].click();", radio_js)
                time.sleep(0.4)
            except Exception:
                print("Opción no disponible, recargando URL...")
                driver.refresh()
                time.sleep(1)
                continue

            # Busqueda de botones de hora:
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Buscando botones de hora...")
            horas = driver.find_elements(By.XPATH, HORA_BTN_XPATH)
            if not horas:
                print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] No hay horas disponibles. Recargando URL... y luego espera 0.3 segundos")
                driver.refresh()
                time.sleep(0.3)
                continue
            hora_seleccionada = False
            for hora_btn in horas:
                try:
                    driver.execute_script("arguments[0].click();", hora_btn)
                    time.sleep(0.4)
                    try:
                        alerta = driver.find_element(By.XPATH, "//div[contains(@class,'v-alert__content') and contains(text(),'Lo sentimos, pero esta hora ya se ha reservado')]")
                        if alerta:
                            print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Hora reservada por otro usuario, intentando siguiente...")
                            continue
                    except:
                        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}]  Hora seleccionada... rellenar datos !")
                        driver.execute_script("document.body.style.zoom='80%'")
                        alarma()
                        alarma()
                        alarma()
                        return True
                except Exception as e:
                    print(f"Error al seleccionar hora: {e}")
            driver.refresh()
            time.sleep(1)
        except Exception as e:
            print(f"Error general en el intento: {e}")
            #mostrar_mensaje(driver, f"Error general en el intento: {e}")
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] No se encontraron horas disponibles en el tiempo de espera ...")
    #mostrar_mensaje(driver, f"[{datetime.now().strftime('%H:%M:%S.%f')}] No se encontraron horas disponibles en el tiempo de espera ...")
    return False 


def main():

    hora_inicio = datetime.combine(datetime.today(), datetime.strptime(hora_de_inicio, "%H:%M:%S").time())  
    hora_final= datetime.combine(datetime.today(), datetime.strptime(hora_de_final, "%H:%M:%S").time())   

    # Cargar el navegador Brave y la WEB
    options = webdriver.ChromeOptions()
    options.binary_location = BRAVE_PATH
    options.add_argument("--start-maximized")      # Pantalla maximizada
    options.add_argument("--disable-infobars")     # Oculta la barra de información
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL) 
    driver.execute_script("document.body.style.zoom='80%'")    # Establecer zoom 

    # Esperar hasta que la hora de inicio de la web sea alcanzada.. (entre las 9am y la 1pm)
   
    while datetime.now() < hora_inicio:
        time.sleep(1)

    """ Bucle principal para intentar obtener la cita. Avisa con un sonido si se encuentra una hora disponible.
        Se ejecuta hasta que se alcance la hora final o se encuentre una cita:
    """
    cita_obtenida = False
    try:
        while datetime.now() < hora_final:
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')}]    esperando la hora ...")
            esperar_hora(segundos_antes)
            if ejecutar_intentos(driver):
                print("Hora obtenida!")
                winsound.Beep(1000, 2000)
                cita_obtenida = True
                break
    finally:
        if not cita_obtenida:
            driver.quit()
                    
if __name__ == "__main__":
    # Si el archivo no existe, lo crea con el valor por defecto
    if not os.path.exists(URL_FILE):
        with open(URL_FILE, "w") as f:
            f.write(DEFAULT_URL)

    # Lee el valor desde el archivo
    with open(URL_FILE, "r") as f:
        URL = f.read().strip()
    main()


    """
    # Comprobar si la opción está disponible y hacer click
    try:
        radio = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.XPATH, OPCION_XPATH))
        )
        driver.execute_script("arguments[0].click();", radio)
        print("Click realizado sobre la opción de asistencia telefónica.")
        time.sleep(5)
    except Exception:
        """