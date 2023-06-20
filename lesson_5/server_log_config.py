import logging
import logging.handlers

import sys
import os
basedir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(basedir)

from lesson_3.global_vars import LOGGER_STR_FORMAT, LOGGER_DATE_FORMAT, ENCODING

formatter = logging.Formatter(fmt=LOGGER_STR_FORMAT, datefmt=LOGGER_DATE_FORMAT)
LOG_FILE = os.path.join(basedir, 'lesson_5', 'server.log')

server_logger = logging.getLogger('server')
server_logger.setLevel(logging.DEBUG)
time_rotating_handler = logging.handlers.TimedRotatingFileHandler(
    filename=LOG_FILE,
    encoding=ENCODING,
    when='D',
    interval=1,
    backupCount=7,
)
time_rotating_handler.setFormatter(formatter)
server_logger.addHandler(time_rotating_handler)


stream_logger = logging.getLogger('stream')
stream_logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
stream_logger.addHandler(stream_handler)


if __name__ == '__main__':
    server_logger.debug('run server_log_config.py module')