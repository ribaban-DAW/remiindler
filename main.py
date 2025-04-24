from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
from dotenv import load_dotenv
import os
import sys

class Logger:

    def __init__(self):
        init()

    def error(self, msg):
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}{msg}", file = sys.stderr)

    def warning(self, msg):
        print(f"{Fore.YELLOW}[WARNING] {Style.RESET_ALL}{msg}", file = sys.stderr)

    def info(self, msg):
        print(f"{Fore.GREEN}[INFO] {Style.RESET_ALL}{msg}")


logger = Logger()


class Assignment:

    def __init__(self, id, name, text, date, url):
        self.id = id
        self.name = name
        self.text = text
        self.date = date
        self.url = url
        self.assignments = []

    def print(self):
        print(f"{Fore.YELLOW}ID {self.id} ({self.name}): {Style.RESET_ALL}[{self.text} ({self.date})]({Fore.BLUE}{self.url}{Style.RESET_ALL})")

class Remiindler:

    def __init__(self, subject_url, subject_ids):
        self._setup()
        self.subject_url = subject_url
        self.subject_ids = subject_ids
        self.assignments = []

    def scrap_assignments(self, driver):
        self._login(driver)
        logger.info("Getting missing assignments...")

        for id in self.subject_ids:
            driver.get(self.subject_url + str(id))
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "generaltable")))

            table = driver.find_element(By.CLASS_NAME, "generaltable")
            rows = table.find_elements(By.XPATH, ".//tr")
            for row in rows:
                if any(x in row.text.lower() for x in self.blacklist) or "no entregado" not in row.text.lower():
                    continue
                anchor = row.find_element(By.TAG_NAME, "a")
                url = "" if not anchor else anchor.get_attribute("href")
                text = "" if not anchor else anchor.text

                column = row.find_element(By.XPATH, "//td[@class='cell c2']")
                date = "" if not column else column.text
                assignment = Assignment(id, self.subject_ids[id], text, date, url)
                self.assignments.append(assignment)
                assignment.print()

        return self.assignments

    def _setup(self):
        blacklist_filename = "blacklist.txt"

        argc = len(sys.argv)
        if (argc > 1):
            flag = sys.argv[1]
            if flag == "-b" or flag == "--blacklist":
                if argc < 3:
                    logger.error("Blacklist file not provided")
                    sys.exit(1)
                blacklist_filename = sys.argv[2]
            elif flag == "-h" or flag == "--help":
                self.usage()
                sys.exit(0)
            else:
                logger.error("Unrecognised flag, use --help to see the available flags")
                sys.exit(1)

        self.set_blacklist(blacklist_filename)

        load_dotenv()
        self.username = self._parse_env("ENV_USER")
        self.password = self._parse_env("ENV_PASS")

    def _usage(self):
        print(f"""Usage: python3 {sys.argv[0]} [FLAG]... [FILE]...
Example: python3 {sys.argv[0]} -b blacklist.txt

Available FLAGS:
-b, --blacklist <file>          Use <file> as blacklist file to avoid matching the words contained in it
-h, --help                      Display this information""")

    def set_blacklist(self, blacklist_filename = "blacklist.txt"):
        if not os.path.isfile(blacklist_filename):
            logger.warning("Can't open the blacklist, ignoring...")
            blacklist_filename = ""

        self.blacklist = []
        if blacklist_filename != "":
            self.blacklist = (''.join(open(blacklist_filename, 'r')).lower()).split('\n')
            self.blacklist.pop(len(self.blacklist) - 1)
            logger.info("Blacklist loaded")

    # Quick and simple parser to avoid problems with especial characters
    def _parse_env(self, env_var):
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

    def _login(self, driver):
        logger.info("Logging in...")
        login_url = "https://edea.juntadeandalucia.es/cas/login?service=https%3A%2F%2Feducacionadistancia.juntadeandalucia.es%2Fcentros%2Fmalaga%2Flogin%2Findex.php%3FauthCAS%3DCAS"
        driver.get(login_url)
        wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        user_input = driver.find_element(By.ID, "username")
        user_input.send_keys(self.username)
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(self.password)
        login_btn = driver.find_element(By.CLASS_NAME, "btn-submit")
        login_btn.click()


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    return driver


if __name__ == "__main__":
    subject_url = "https://educacionadistancia.juntadeandalucia.es/centros/malaga/mod/assign/index.php?id="
    subject_ids = {9051: "Sostenibilidad", 4011: "BBDD", 6585: "Entornos", 6584: "LDM", 4162: "Digitalización", 4161: "IPE", 4008: "Programación", 4000: "Sistemas"}

    remiindler = Remiindler(subject_url, subject_ids)
    driver = None

    try:
        driver = setup_driver()
        assignments = remiindler.scrap_assignments(driver)

    except Exception as e:
        if driver:
            print(e)
        else:
            print("Couldn't setup the driver", file=sys.stderr)

    finally:
        if driver:
            driver.quit()
