import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

<<<<<<< HEAD

def os_env():
=======
def get_os_env():
>>>>>>> put os_env into var to make sure it's not called 4 times
    from sys import platform

    if platform == "linux" or platform == "linux2":
        return "linux"
    elif platform == "darwin":
        return "osx"
    elif platform == "win32":
        return "windows"


class Settings:
<<<<<<< HEAD
    log_location = os.path.join(BASE_DIR, "logs")
    database_location = os.path.join(BASE_DIR, "db", "instapy.db")
=======
    log_location = os.path.join(BASE_DIR, 'logs')
    database_location = os.path.join(BASE_DIR, 'db', 'instapy.db')
    os_env = get_os_env()
>>>>>>> put os_env into var to make sure it's not called 4 times

    chromedriver_location = os.path.join(BASE_DIR, "assets", "chromedriver")

<<<<<<< HEAD
    if os_env() == "osx":
        chromedriver_location = os.path.join(BASE_DIR, "assets", "chromedriver_osx")

    if os_env() == "linux":
        chromedriver_location = os.path.join(BASE_DIR, "assets", "chromedriver_linux")

    if os_env() == "windows":
        chromedriver_location = os.path.join(BASE_DIR, "assets", "chromedriver_windows")
=======
    if os_env == 'osx':
        chromedriver_location = os.path.join(BASE_DIR, 'assets', 'chromedriver_osx')

    if os_env == 'linux':
        chromedriver_location = os.path.join(BASE_DIR, 'assets', 'chromedriver_linux')

    if os_env == 'windows':
        chromedriver_location = os.path.join(BASE_DIR, 'assets', 'chromedriver_windows')
>>>>>>> put os_env into var to make sure it's not called 4 times

    if not os.path.exists(chromedriver_location):
        chromedriver_location = os.path.join(BASE_DIR, "assets", "chromedriver")

    chromedriver_min_version = 2.36
    # Set a logger cache outside the InstaPy object to avoid re-instantiation issues
    loggers = {}
    logger = None
    # Set current profile credentials for DB operations
    profile = {"id": None, "name": None}
