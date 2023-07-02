import logging.handlers
import os.path

from common.variables import LOGGING_LEVEL

server_logger = logging.getLogger("server")
formatter = logging.Formatter("%(asctime)s %(levelname)-10s %(module)s %(message)s")

path = os.path.join(os.path.abspath(".."), "log", "server_log.log")
file_handler = logging.handlers.TimedRotatingFileHandler(path, encoding="utf8", interval=1, when="D")
file_handler.setFormatter(formatter)

server_logger.addHandler(file_handler)
server_logger.setLevel(LOGGING_LEVEL)

if __name__ == "__main__":
    server_logger.critical("Критическая ошибка")
    server_logger.error("Ошибка")
    server_logger.debug("Отладочная информация")
    server_logger.info("Информационное сообщение")