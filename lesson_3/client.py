from socket import *
import time
import json
import argparse
import ipaddress

import os
import sys
basedir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(basedir)

from lesson_3.global_vars import *
from lesson_5.client_log_config import client_logger


def presence_msg(username=None, password=None, status='online'):
    msg = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': username,
            'password': password,
            'status': status
        }
    }
    client_logger.debug('Сформировано "presence" сообщение для сервера')
    return json.dumps(msg).encode(ENCODING)


def preparing_message(msg: str, action: str = 'msg', ):
    """Готовит сообщение серверу"""
    data = {
        'action': action,
        'time': time.time(),
        'message': msg,
    }
    client_logger.debug(f'Подготовлено сообщение {data}')
    return json.dumps(data).encode(ENCODING)


def send_message(s: socket, msg: bytes):
    try:
        s.send(msg)
        client_logger.debug('Сообщение отправлено')
    except Exception as ex:
        client_logger.error(f'Ошибка при отправке сообщения {ex}')


def get_response(s: socket, max_length=BUFFERSIZE):
    msg = s.recv(max_length).decode(ENCODING)
    client_logger.debug(f'Получено сообщение от сервера {msg}')
    return msg


def parse_response(msg: str):
    try:
        obj = json.loads(msg)
        client_logger.debug(f'Сформирован объект из сообщения от сервера: {obj}')
    except Exception as ex:
        client_logger.error(f'Ошибка при разборке сообщения. {ex}')
        return
    return obj


def start(address, port):
    client_logger.debug(f'Запущен клиент с параметрами: ip = {address}, port = {port}')
    while True:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((address, port))
        pm = presence_msg()
        send_message(s, pm)
        client_logger.debug(f'Отправлено "presence" сообщение!')
        msg = input('>>> ')
        send_message(s, preparing_message(msg))
        client_logger.debug(f'Отправлено сообщение {msg}')

        resp = parse_response(get_response(s))
        client_logger.debug(f'Получен ответ {resp}')
        print('<<<', resp['response'])
        s.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('address', type=str, help='IP-адрес сервера')
    parser.add_argument('-p', dest='port', type=int, default=7777, help='TCP-порт на сервере (по умолчанию 7777)')
    args = parser.parse_args()

    try:
        ipaddress.ip_address(args.address)
    except ValueError:
        parser.error('Введен не корректный ip адрес')

    start(args.address, args.port)