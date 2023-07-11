import logging
import os.path

from common.variables import LOGGING_LEVEL

client_logger = logging.getLogger("client")
formatter = logging.Formatter("%(asctime)s %(levelname)-10s %(module)s %(message)s")

path = os.path.join(os.path.abspath(".."), "log", "client_log.log")
file_handler = logging.FileHandler(path, encoding="utf8")
file_handler.setFormatter(formatter)

client_logger.addHandler(file_handler)
client_logger.setLevel(LOGGING_LEVEL)

if __name__ == "__main__":
    client_logger.critical("Критическая ошибка")
    client_logger.error("Ошибка")
    client_logger.debug("Отладочная информация")
    client_logger.info("Информационное сообщение")