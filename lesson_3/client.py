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