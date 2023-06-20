import select
from socket import socket, AF_INET, SOCK_STREAM
import argparse
import ipaddress

from global_vars import *
from lesson_5.server_log_config import stream_logger, log

from lesson_3.global_vars import *
from lesson_5.server_log_config import server_logger, stream_logger
from global_vars import *

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
    msg = client.recv(BUFFERSIZE).decode(ENCODING)

    server_logger.debug(f'Сообщение от клиента {msg}')
    return json.loads(msg)


def preparing_response(response_code: int, action: str = 'presence'):
    """Готовит ответ клиенту"""
    data = {
        'action': action,
        'time': time.time(),
        'response': response_code,
    }

    server_logger.debug(f'Подготовка ответа {data}')
    return json.dumps(data).encode(ENCODING)

    return responses


def send_message(client, message: bytes):
    try:
        client.send(message)
        server_logger.debug('Сообщение отправлено')
    except Exception as ex:
        server_logger.error(f'Ошибка при отправке сообщения: {ex}')
    client.send(message)

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
        client, addr = s.accept()
        cm = get_message(client)
        print(cm['message'])
        msg = preparing_response(OK)
        send_message(client, msg)
        client.close()


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