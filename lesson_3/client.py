import sys
from socket import *
import argparse
import ipaddress

from global_vars import *
from lesson_5.client_log_config import client_logger, log


def send_message(sock: socket, message: str):
    if message == 'exit':
        sock.close()
        sys.exit(0)
import os
import sys
basedir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(basedir)

from lesson_3.global_vars import *
from lesson_5.client_log_config import client_logger
from global_vars import *


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

    prepare_message = None
    try:
        prepare_message = message.encode(ENCODING)
    except UnicodeEncodeError:
        client_logger.error(f'Не удалось закодировать сообщение - "{message}"')

    if prepare_message:
        try:
            sock.send(prepare_message)
        except:
            client_logger.error(f'Не удалось отправить сообщение {message} клиенту {sock.getpeername()}')


def get_message(s: socket):
    msg_bytes = None
    try:
        msg_bytes = s.recv(BUFFERSIZE)
    except:
        client_logger.error(f'Нет связи с сервером! {s.getpeername()}')

    if msg_bytes:
        try:
            message = msg_bytes.decode(ENCODING)
        except UnicodeDecodeError as e:
            client_logger.error(f'{e}')
        else:
            return message


@log
def start(address, port, mode):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((address, port))
    while True:
        if mode == 'send':
            send_message(s, input('>>> '))
        elif mode == 'listen':
            message = get_message(s)
            if message:
                print(message)
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
    s.send(msg)


def get_response(s: socket, max_length=BUFFERSIZE):
    return s.recv(max_length).decode(ENCODING)


def parse_response(msg: str):
    return json.loads(msg)


def start(address, port):

    while True:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((address, port))
        presence_msg()
        msg = input('>>> ')
        send_message(s, preparing_message(msg))
        resp = parse_response(get_response(s))
        print('<<<', resp['response'])
        s.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('address', type=str, help='IP-адрес сервера')
    parser.add_argument('mode', type=str, help='Тип клиента (send - отправитель, listen - получатель)')
    parser.add_argument('-p', dest='port', type=int, default=7777, help='TCP-порт на сервере (по умолчанию 7777)')
    args = parser.parse_args()

    try:
        ipaddress.ip_address(args.address)
    except ValueError:
        parser.error('Введен не корректный ip адрес')

    start(args.address, args.port, args.mode)