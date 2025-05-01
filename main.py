from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
from dotenv import load_dotenv
from getpass import getpass
import webbrowser
import readline
import os
import sys

class LoggerLevel():
    DEBUG   = 1 << 0
    INFO    = 1 << 1
    WARNING = 1 << 2
    ERROR   = 1 << 3

    NONE = 0
    DEFAULT = INFO | WARNING | ERROR
    ALL = DEBUG | INFO | WARNING | ERROR

class Logger():

    def __init__(self, level = LoggerLevel.DEFAULT):
        init()
        self.level = level

    def debug(self, msg):
        if not LoggerLevel.DEBUG & self.level:
            return
        print(f"{Fore.BLUE}[DEBUG] {Style.RESET_ALL}{msg}")

    def info(self, msg):
        if not LoggerLevel.INFO & self.level:
            return
        print(f"{Fore.GREEN}[INFO] {Style.RESET_ALL}{msg}")

    def warning(self, msg):
        if not LoggerLevel.WARNING & self.level:
            return
        print(f"{Fore.YELLOW}[WARNING] {Style.RESET_ALL}{msg}", file = sys.stderr)

    def error(self, msg):
        if not LoggerLevel.ERROR & self.level:
            return
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}{msg}", file = sys.stderr)


logger = Logger()


class Assignment:

    def __init__(self, id, name, title, date, url):
        self.title = title
        self.date = date
        self.url = url

    def print(self):
        print(f"[{self.title}]({Fore.BLUE}{self.url}{Style.RESET_ALL} | {self.date})")


class Subject:

    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url
        self.assignments = []

    def print(self):
        print(f"{Fore.YELLOW}{self.name} ({self.id}):{Style.RESET_ALL}")
        for assignment in self.assignments:
            print("  ", end="")
            assignment.print()

class Remiindler:

    def __init__(self, subject_base_url, subject_ids):
        self.subject_base_url = subject_base_url
        self.subject_ids = subject_ids
        self.subjects = []
        self._driver = None
        self._is_scrapped = False
        self._wait_time = 5

        self._setup()

    def gui(self):
        logger.warning("TODO")

    def tui(self):
        options = [
            {"name": "Get Assignments", "func": self.get_assignments},
            {"name": "Generate HTML", "func": self.generate_html},
            {"name": "Show Configuration", "func": self.show_config},
            {"name": "Change login data", "func": lambda: self.config_login_data(True)},
            {"name": "Quit"},
        ]

        while True:
            print("\nAvailable options:")
            print("-----------------------")
            for i in range(len(options)):
                print(f"{i + 1}. {options[i]['name']}")
            print("-----------------------")

            try:
                option = int(input("Select an option: "))
                option -= 1
                if option < 0 or option >= len(options):
                    logger.error("Unknown option")
                    continue
                elif option == len(options) - 1:
                    self._driver.quit()
                    print("Bye")
                    return

                try:
                    logger.info(f"Selected '{options[option]['name']}'")
                    options[option]["func"]()
                except Exception as e:
                    logger.error(e)

            except Exception as e:
                logger.error("Unknown option")

    def get_assignments(self, is_forced = False):
        self._scrap_assignments(is_forced)
        for subject in self.subjects:
            subject.print()

    def generate_html(self):
        self._scrap_assignments()
        with open("index.html", "w") as f:
            f.write("""<html>
<head>
<title>Remiindler</title>
<style>
:root {
	color-scheme: dark light;
	--background-primary: #222222;
	--foreground-primary: #dddddd;
}

@media (prefers-color-scheme: light) {
	:root {
		--background-primary: #ddd;
		--foreground-primary: #222;
	}
}

body {
	background-color: var(--background-primary);
	color: var(--foreground-primary);
}
</style>
<link href='styles.css' rel='stylesheet'>
</head>
<body>
""")
            for subject in self.subjects:
                subject.name
                f.write(f"<h1>{subject.name}</h1>")
                for assignment in subject.assignments:
                    f.write(f"<p><a href='{assignment.url}' target='_blank' rel='noopener noreferrer' >{assignment.title}</a> | {assignment.date}</p>")
            f.write("</body>\n</html>")
        logger.info("'index.html' generated")
        webbrowser.open("index.html")

    def show_config(self):
        logger.warning("TODO")

    def config_login_data(self, is_forced = False):
        self.username = self._parse_data(self._get_login_data("ENV_USERNAME", is_forced))
        self.password = self._parse_data(self._get_login_data("ENV_PASSWORD", is_forced))

    def _get_login_data(self, env_var, is_forced = False):
        if is_forced:
            data = getpass(f"Introduce your {env_var[4:].lower()}: ")
            return

        data = os.getenv(env_var)
        if data == None:
            logger.warning(f"Couldn't find '{env_var}'")
            data = getpass(f"Introduce your {env_var[4:].lower()}: ")

        return data

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
                self._usage()
                sys.exit(0)
            else:
                logger.error("Unrecognised flag, use --help to see the available flags")
                sys.exit(1)

        self._set_blacklist(blacklist_filename)

        load_dotenv()
        self.config_login_data()

        try:
            self._driver = self._setup_driver()
        except Exception as e:
            logger.error("Couldn't setup the driver")

    def _usage(self):
        logger.info(f"""Usage: python3 {sys.argv[0]} [FLAG]... [FILE]...

Example: python3 {sys.argv[0]} -b blacklist.txt

Available FLAGS:
-b, --blacklist <file>          Use <file> as blacklist file to avoid matching the words contained in it
-h, --help                      Display this information""")

    def _set_blacklist(self, blacklist_filename = "blacklist.txt"):
        if not os.path.isfile(blacklist_filename):
            logger.warning("Can't open the blacklist, ignoring...")
            blacklist_filename = ""

        self.blacklist = []
        if blacklist_filename != "":
            self.blacklist = (''.join(open(blacklist_filename, 'r')).lower()).split('\n')
            self.blacklist.pop(len(self.blacklist) - 1)
            logger.info("Blacklist loaded")

    # Quick and simple parser to avoid problems with especial characters
    def _parse_data(self, data):
        escaped = False
        parsed_data = ""

        for c in data:
            if not escaped and c == '\\':
                escaped = True
                continue
            parsed_data += c
            escaped = False

        return parsed_data

    def _login(self, retry = 3):
        if retry <= 0:
            raise Exception("Too many retries...")

        expected_url = "https://educacionadistancia.juntadeandalucia.es/centros/malaga/my/"
        if self._driver.current_url == expected_url:
            return

        logger.info("Logging in...")
        login_url = "https://edea.juntadeandalucia.es/cas/login?service=https%3A%2F%2Feducacionadistancia.juntadeandalucia.es%2Fcentros%2Fmalaga%2Flogin%2Findex.php%3FauthCAS%3DCAS"
        self._driver.get(login_url)
        WebDriverWait(self._driver, self._wait_time).until(EC.presence_of_element_located((By.ID, "username")))

        user_input = self._driver.find_element(By.ID, "username")
        user_input.send_keys(self.username)
        logger.debug("Introduced username")
        password_input = self._driver.find_element(By.ID, "password")
        password_input.send_keys(self.password)
        logger.debug("Introduced password")
        login_btn = self._driver.find_element(By.CLASS_NAME, "btn-submit")
        login_btn.click()

        try:
            WebDriverWait(self._driver, self._wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "menu-logo-nombre")))
        except:
            if self._driver.current_url != expected_url:
                raise Exception("Incorrect username/password, try to reconfigure it!")
            else:
                logger.error("Couldn't load the page. Trying again...")
                self._login(retry - 1)
        logger.debug("Logged in")

    def _scrap_assignments(self, is_forced = False):
        if self._is_scrapped and not is_forced:
            return

        self._login()

        index = 0
        for id in self.subject_ids:
            subject_url = self.subject_base_url + str(id)
            subject = Subject(id, self.subject_ids[id], subject_url)
            logger.info(f"Scrapping '{subject.name}' missing assignments...")
            self.subjects.append(subject)

            logger.debug(f"Subject URL: {subject_url}")
            self._driver.get(subject_url)
            WebDriverWait(self._driver, self._wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "generaltable")))

            table = self._driver.find_element(By.CLASS_NAME, "generaltable")
            rows = table.find_elements(By.XPATH, ".//tr")
            for row in rows:
                if any(x in row.text.lower() for x in self.blacklist) or ("no entregado" not in row.text.lower() and "sin entrega" not in row.text.lower()):
                    continue
                anchor = row.find_element(By.TAG_NAME, "a")
                url = "" if not anchor else anchor.get_attribute("href")
                text = "" if not anchor else anchor.text

                column = row.find_element(By.XPATH, "//td[@class='cell c2']")
                date = "" if not column else column.text
                assignment = Assignment(id, self.subject_ids[id], text, date, url)
                self.subjects[index].assignments.append(assignment)
            index += 1

        self._is_scrapped = True

    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)

        return driver


if __name__ == "__main__":
    subject_url = "https://educacionadistancia.juntadeandalucia.es/centros/malaga/mod/assign/index.php?id="
    subject_ids = {
        9051: "Sostenibilidad",
        4011: "Base de Datos",
        6585: "Entornos de Desarrollo",
        6584: "Lenguaje de Marcas",
        4162: "Digitalización",
        4161: "IPE",
        4008: "Programación",
        4000: "Sistemas Informáticos",
    }

    remiindler = Remiindler(subject_url, subject_ids)
    remiindler.tui()
