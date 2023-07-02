import sys
import inspect

from log_config.server_log_config import *
from log_config.client_log_config import *
from log_config.console_log_config import *


def log(func):
    if sys.argv[0].endswith("client.py"):
        logger = logging.getLogger("client")
    elif sys.argv[0].endswith("server.py"):
        logger = logging.getLogger("server")
    else:
        logger = logging.getLogger("console")

    def log_wraper(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.info(f" Функция {func.__name__}() вызвана из функции {inspect.stack()[1][3]}()")
        return result
    return log_wraper


if __name__ == "__main__":
    @log
    def func_z():
        pass

    def main():
        func_z()

    main()