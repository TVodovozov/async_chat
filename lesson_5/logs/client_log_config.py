import logging
import inspect

import sys
import os
basedir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(basedir)

from global_vars import LOGGER_STR_FORMAT, LOGGER_DATE_FORMAT

LOG_FILE = os.path.join(basedir, 'logs', 'client.log')

client_logger = logging.getLogger('client')
client_logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(LOG_FILE)
ch.setFormatter(logging.Formatter(fmt=LOGGER_STR_FORMAT, datefmt=LOGGER_DATE_FORMAT))
client_logger.addHandler(ch)


def log(f):
    def wrapper(*args, **kwargs):
        current_frame = inspect.currentframe()
        from_line = current_frame.f_back.f_lineno
        module = current_frame.f_back.f_code.co_filename
        caller_func = current_frame.f_back.f_code.co_name
        client_logger.info(f'Вызвана функция {f.__name__}, с параметрами args = {args}, kwargs = {kwargs},\t'
                        f'[вызывающий модуль {module}]\t'
                        f'[вызывающая функция {caller_func}]\t'
                        f'[вызвана в строке {from_line}]\t')
        return f(*args, **kwargs)
    return wrapper


if __name__ == '__main__':
    client_logger.debug('run client_log_config.py module')