import tempfile
import logging

LOG_FILE = "/tmp/lightning-station.log"

def setup_log(console):
    #print(console)
    logging.CONSOLE = console
    logging.basicConfig(filename=LOG_FILE, filemode='w', level=logging.INFO)

def log(string):
    #print(logging.CONSOLE)
    if logging.CONSOLE:
        print(string)
    logging.info(str(string))

