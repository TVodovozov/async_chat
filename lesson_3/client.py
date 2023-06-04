from socket import *
import time
import json
import argparse
import ipaddress

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
    return json.dumps(msg).encode(ENCODING)


def preparing_message(msg: str, action: str = 'msg', ):
    """Готовит сообщение серверу"""
    data = {
        'action': action,
        'time': time.time(),
        'message': msg,
    }
    return json.dumps(data).encode(ENCODING)


def send_message(s: socket, msg: bytes):
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
    parser.add_argument('-p', dest='port', type=int, default=7777, help='TCP-порт на сервере (по умолчанию 7777)')
    args = parser.parse_args()

    try:
        ipaddress.ip_address(args.address)
    except ValueError:
        parser.error('Введен не корректный ip адрес')

    start(args.address, args.port)