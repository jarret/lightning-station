import tempfile
import logging
from logging.handlers import RotatingFileHandler

DEFAULT_LOG_FILE = "/tmp/lightning-station.log"

def setup_log(console, log_file):
    #print(console)
    logging.CONSOLE = console
    logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)
    log = logging.getLogger()
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=1)
    log.addHandler(handler)


def log(string):
    #print(logging.CONSOLE)
    if logging.CONSOLE:
        print(string)
    logging.info(str(string))
