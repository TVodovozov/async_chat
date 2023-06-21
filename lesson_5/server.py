from socket import *
import time
import json
import argparse
import ipaddress

from global_vars import *
from lesson_5.logs.server_log_config import server_logger, stream_logger, log


@log
def get_message(client):
    """
    Получает сообщение от клиента
    :param client:
    :return: строку сообщения
    """
    try:
        msg = client.recv(BUFFERSIZE).decode(ENCODING)
    except UnicodeDecodeError:
        server_logger.error(f'Ошибка декодирования сообщения {msg}')
        msg = {
            'action': 'msg',
            'response': BAD_REQUEST,
            'error': 'UnicodeDecodeError'
        }
    return json.loads(msg)


@log
def preparing_response(response_code: int, action: str = 'presence'):
    """Готовит ответ клиенту"""
    data = {
        'action': action,
        'time': time.time(),
        'response': response_code,
    }
    server_logger.debug(f'Подготовка ответа {data}')
    return json.dumps(data).encode(ENCODING)


@log
def send_message(client, message: bytes):
    try:
        client.send(message)
        server_logger.debug('Сообщение отправлено')
    except Exception as ex:
        server_logger.error(f'Ошибка при отправке сообщения: {ex}')


@log
def get_socket(address: str, port: int, listen: int = 5):
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.listen(listen)
    server_logger.debug(f'Запущен сервер с параметрами: ip = {address}, port = {port}, listen = {listen}')
    return s


@log
def start(address: str, port: int):
    s = get_socket(address, port)

    while True:
        server_logger.debug('Ожидание подключения клиента')
        client, addr = s.accept()
        server_logger.debug(f'Подключен клиент: {client}, с адресом {addr}')
        cm = get_message(client)  # Получение presence сообщения
        server_logger.debug(f'Получено сообщение от клиента: {cm}')

        cm = get_message(client)  # Получение сообщения
        if cm.get('message'):
            stream_logger.info(cm.get('message'))

        msg = preparing_response(OK)
        send_message(client, msg)
        client.close()
        server_logger.info(f'Закрыто соединение с клиентом: {client}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', dest='port', type=int, default=7777,
                        help='TCP-порт для работы (по умолчанию использует 7777)')
    parser.add_argument('-a', dest='address',
                        help='IP-адрес для прослушивания (по умолчанию слушает все доступные адреса)')
    args = parser.parse_args()

    address = args.address or ''
    if address:
        try:
            ipaddress.ip_address(address)
        except ValueError:
            parser.error(f'Введен не корректный ip адрес "{address}"')

    start(address, args.port)