from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
from dotenv import load_dotenv
import os

load_dotenv()

username=os.getenv("ENV_USER")
pwd=os.getenv("ENV_PASS")
login_url="https://edea.juntadeandalucia.es/cas/login?service=https%3A%2F%2Feducacionadistancia.juntadeandalucia.es%2Fcentros%2Fmalaga%2Flogin%2Findex.php%3FauthCAS%3DCAS"
subject_url="https://educacionadistancia.juntadeandalucia.es/centros/malaga/mod/assign/index.php?id="
ids={9051: "Sostenibilidad", 4011: "BBDD", 6585: "Entornos", 6584: "LDM", 4162: "Digitalización", 4161: "IPE", 4008: "Programación", 4000: "Sistemas"}
blacklist=["examen", "jugar", "escape room", "resultados", "subnetting", "cidr", "vlsm", "supercomputadoras", "isla", "mapa", "juguemos"]

init()

try:
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    driver.get(login_url)
    wait = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )

    # Login
    user_input = driver.find_element(By.ID, "username")
    user_input.send_keys(username)
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(pwd)
    login_btn = driver.find_element(By.CLASS_NAME, "btn-submit")
    login_btn.click()

    # Get missing assignments
    for key in ids:
        driver.get(subject_url+str(key))
        wait = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "generaltable"))
        )

        table = driver.find_element(By.CLASS_NAME, "generaltable")
        rows = table.find_elements(By.XPATH, ".//tr")
        for row in rows:
            if any(x in row.text.lower() for x in blacklist) or "no entregado" not in row.text.lower():
                continue
            print(f"{Fore.YELLOW}{ids[key]}: {Fore.WHITE}{row.text}{Style.RESET_ALL}")

except Exception as e:
    print(e)

finally:
    driver.quit()
