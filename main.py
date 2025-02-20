from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
from dotenv import load_dotenv
import os
import sys

def log_error(msg):
    print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}{msg}", file = sys.stderr)

def log_info(msg):
    print(f"{Fore.GREEN}[INFO] {Style.RESET_ALL}{msg}")

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
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    return driver

def login(driver, username, password):
    log_info("Logging in...")
    login_url = "https://edea.juntadeandalucia.es/cas/login?service=https%3A%2F%2Feducacionadistancia.juntadeandalucia.es%2Fcentros%2Fmalaga%2Flogin%2Findex.php%3FauthCAS%3DCAS"
    driver.get(login_url)
    wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    user_input = driver.find_element(By.ID, "username")
    user_input.send_keys(username)
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)
    login_btn = driver.find_element(By.CLASS_NAME, "btn-submit")
    login_btn.click()

def get_missing_assignments(driver, blacklist_filename):
    log_info("Getting missing assignments...")
    subject_url = "https://educacionadistancia.juntadeandalucia.es/centros/malaga/mod/assign/index.php?id="
    blacklist = (''.join(open(blacklist_filename, 'r')).lower()).split('\n')
    blacklist.pop(len(blacklist) - 1)
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
            print(f"{Fore.YELLOW}{ids[key]}: {Style.RESET_ALL}{row.text}")

    return assignments

if __name__ == "__main__":
    blacklist_filename = "blacklist.txt"
    argc = len(sys.argv)
    if (argc > 1):
        flag = sys.argv[1]
        if flag == "-b" or flag == '--blacklist':
            if argc < 3:
                log_error("Blacklist file not provided")
                sys.exit(1)
            blacklist_filename = sys.argv[2]
            if not os.path.isfile(blacklist_filename):
                log_error("Can't open the blacklist")
                sys.exit(1)
        elif flag == "-h" or flag == "--help":
            print(f"""Usage: python3 {sys.argv[0]} [FLAG]... [FILE]...
Example: python3 {sys.argv[0]} -b blacklist.txt

Available FLAGS:
  -b, --blacklist <file>          Use <file> as blacklist file to avoid matching the words contained in it
  -h, --help                      Display this information""")
            sys.exit(0)
        else:
            log_error("Unrecognised flag, use --help to see the available flags")
            sys.exit(1)

    load_dotenv()
    username = parse_env("ENV_USER")
    password = parse_env("ENV_PASS")
    init()
    driver = None

    try:
        driver = setup_driver()
        login(driver, username, password)
        assignments = get_missing_assignments(driver, blacklist_filename)

    except Exception as e:
        if driver:
            print(e)
        else:
            print("Couldn't setup the driver", file=sys.stderr)

    finally:
        if driver:
            driver.quit()
