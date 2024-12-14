from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
from dotenv import load_dotenv
import os

# Quick and simple parser to avoid problems with especial characters
def parse_env(env_var):
    data = os.getenv(env_var)
    escaped = False
    parsed_data = ""

    for c in data:
        if not escaped and c == '\\':
            escaped = True
            continue
        parsed_data += c
        escaped = False

    return parsed_data

def setup_driver():
    dev_flag = False

    if dev_flag:
        # I still have to figure out a global way to do it, maybe installing a browser locally
        options = webdriver.FirefoxOptions()
        options.browser_location = "/usr/bin/firefox"
        service = webdriver.firefox.service.Service(executable_path="/snap/bin/geckodriver")
        driver = webdriver.Firefox(service=service, options=options)
    else:
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)

    return driver

def login(driver, username, password):
    login_url = "https://edea.juntadeandalucia.es/cas/login?service=https%3A%2F%2Feducacionadistancia.juntadeandalucia.es%2Fcentros%2Fmalaga%2Flogin%2Findex.php%3FauthCAS%3DCAS"
    driver.get(login_url)
    wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    user_input = driver.find_element(By.ID, "username")
    user_input.send_keys(username)
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)
    login_btn = driver.find_element(By.CLASS_NAME, "btn-submit")
    login_btn.click()

# Right now it also prints missing assignments
def get_assignments(driver):
    subject_url = "https://educacionadistancia.juntadeandalucia.es/centros/malaga/mod/assign/index.php?id="
    blacklist = ["examen", "jugar", "escape room", "resultados", "subnetting", "cidr", "vlsm", "supercomputadoras", "isla", "mapa", "juguemos"]
    ids = {9051: "Sostenibilidad", 4011: "BBDD", 6585: "Entornos", 6584: "LDM", 4162: "Digitalización", 4161: "IPE", 4008: "Programación", 4000: "Sistemas"}
    assignments = []

    for key in ids:
        driver.get(subject_url + str(key))
        wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "generaltable")))

        table = driver.find_element(By.CLASS_NAME, "generaltable")
        rows = table.find_elements(By.XPATH, ".//tr")
        for row in rows:
            if any(x in row.text.lower() for x in blacklist) or "no entregado" not in row.text.lower():
                continue
            assignments.append({ids[key]: row.text})
            print(f"{Fore.YELLOW}{ids[key]}: {Fore.WHITE}{row.text}{Style.RESET_ALL}")

    return assignments

def main():
    load_dotenv()
    username = parse_env("ENV_USER")
    password = parse_env("ENV_PASS")
    init()
    driver = None

    try:
        driver = setup_driver()
        login(driver, username, password)
        assignments = get_assignments(driver)

    except Exception as e:
        if driver:
            print(e)
        else:
            print("Couldn't setup the driver")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
