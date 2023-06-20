import select
from socket import socket, AF_INET, SOCK_STREAM
import argparse
import ipaddress

from global_vars import *
from lesson_5.server_log_config import stream_logger, log


def read_requests(r_clients: list, all_clients: list):
    """
    Читает запросы из списка клиентов.
    Возвращает словарь вида {сокет: запрос}
    """

    responses = {}
    for sock in r_clients:
        try:
            data = sock.recv(BUFFERSIZE).decode(ENCODING)
            responses[sock] = data
        except:
            stream_logger.info(f'Клиент {sock} отключился')
            all_clients.remove(sock)

    return responses


def write_responses(requests, w_clients, all_clients):
    for sock in w_clients:
        try:
            # Отправляем на каждый доступный сокет все сообщения из requests
            for resp in requests.values():
                sock.send(resp.encode(ENCODING))
        except:
            stream_logger.info(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
            sock.close()
            all_clients.remove(sock)



@log
def start(address: str, port: int):
    clients = []

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.listen(5)
    s.settimeout(0.2)

    while True:
        try:
            clt, addr = s.accept()
        except OSError:
            pass
        else:
            stream_logger.info(f'Получен запрос на соединение от {addr}')
            clients.append(clt)
        finally:
            wait = 0
            rlist = []
            wlist = []
            try:
                rlist, wlist, erlist = select.select(clients, clients, [], wait)
            except:
                pass

            requests = read_requests(rlist, clients)
            if requests:
                write_responses(requests, wlist, clients)


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