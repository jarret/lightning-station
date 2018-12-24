import logging
from eink_ui import EinkUI

logging.CONSOLE = True
eu = EinkUI()

#print(eu.gen_qrcode_bytes().hex())
print(eu.gen_screen_bytes())
