import logging

import sys
import os
basedir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(basedir)

from lesson_3.global_vars import LOGGER_STR_FORMAT, LOGGER_DATE_FORMAT

LOG_FILE = os.path.join(basedir, 'lesson_5', 'client.log')

client_logger = logging.getLogger('client')
client_logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(LOG_FILE)
ch.setFormatter(logging.Formatter(fmt=LOGGER_STR_FORMAT, datefmt=LOGGER_DATE_FORMAT))
client_logger.addHandler(ch)


if __name__ == '__main__':
    client_logger.debug('run client_log_config.py module')