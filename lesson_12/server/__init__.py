import json
import select
from json import JSONDecodeError
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from typing import Optional

from jsonschema.exceptions import ValidationError

from .contacts import Contacts
from .logger import logger
from tools.validator import Validator
from tools.responses import error_400, error_500, ok, RESPONSE
from tools.requests import request_msg
from tools.descriptors import Port
from metaclass import ServerVerifier
from storage.server import ServerDB


class ChatServer(Thread):
    port = Port()

    def __init__(self, config):
        self.clients = {}
        self.socket = None
        self.address = config["address"]
        self.port = config["port"]
        self.listen = config["listen"]
        self.timeout = config["timeout"]
        self.validator = Validator(config["schema"])
        self.encoding = config["encoding"]
        self.limit = config["input_limit"]
        self.select_wait = config["select_wait"]
        self.db = ServerDB("server.db")
        self.contacts = Contacts(self.db)
        super().__init__()

    def __del__(self):
        self.close()

    def close(self):
        msg = request_msg(sender="server", to="global", encoding=self.encoding, message="Сервер выключился!")
        for client in self.clients:
            try:
                self.send_data(client=client, data=msg)
                client.close()
            except ConnectionResetError:
                pass
        self.db.Contacts.drop_table()
        self.db.close()
        if self.socket is not None:
            self.socket.close()

    def init(self):
        self.db.init()
        # Принудительная очистка списка пользователей
        self.db.Contacts.drop_table()
        self.db.Contacts.create_table()
        self.clients = {}

        self.__init_socket()

    def __init_socket(self):
        _socket = socket(AF_INET, SOCK_STREAM)
        _socket.bind((self.address, self.port))
        _socket.settimeout(self.timeout)
        self.socket = _socket
        self.socket.listen(self.listen)
        logger.info("Server started at {address}:{port}, timeout={timeout}, listen={listen}".format(
            address=self.address, port=self.port, timeout=self.timeout, listen=self.listen
        ))

    def get_data(self, *, client: socket) -> dict:
        try:
            data = client.recv(self.limit).decode(self.encoding)
            data = json.loads(data)
            return data
        except ConnectionResetError:
            logger.info(str(client.getpeername()) + " disconnected")
            self.clients.pop(client)

    def send_data(self, *, client: socket, data: dict):
        data = json.dumps(data).encode(self.encoding)
        client.send(data)

    def action(self, client: socket, data: dict) -> Optional[dict]:
        msg = None
        action = data["action"]
        if action == "msg":
            if self.validator.validate_data(action, data):
                msg = data
        elif action == "presence":
            if self.validator.validate_data(action, data):
                self.send_data(client=client, data=ok())
        elif action == "authenticate":
            if self.validator.validate_data(action, data):
                if data["user"].get("password", None) is not None:
                    if self.login(data[["user"]], client):
                        self.send_data(client=client, data=ok())
                    else:
                        self.send_data(client=client, data=error_400(code=409))
        elif action in ["add_contact", "del_contact", "get_contacts"]:
            if self.validator.validate_data("contacts", data):
                result = self.contacts(data, client)
                if isinstance(result, bool):
                    if result:
                        self.send_data(client=client, data=ok())
                    else:
                        self.send_data(client=client, data=error_400())
                else:
                    self.send_data(client=client, data=ok(str(result), code=202))
        elif action == "quit":
            if client in self.clients:
                msg = request_msg(
                    sender="server", to="global", encoding=self.encoding,
                    message="Пользователь: {user}, покинул чат!".format(user=self.clients[client])
                )
            self.quite(client, ok("Goodbye!"))
        elif action == "join":
            pass
        elif action == "leave":
            pass
        return msg

    def quite(self, client: socket, msg: dict):
        if client in self.clients:
            self.clients.pop(client)
            self.send_data(client=client, data=msg)
            client.close()
            self.db.Contacts.delete_by_client(self.db.Clients.name == self.clients[client])

    def writer(self, clients: list[socket], msgs: dict):
        for sender, msg in msgs.items():
            if msg["to"] == "#server":
                for client in clients:
                    try:
                        self.send_data(client=client, data=msg)
                    except ConnectionResetError:
                        if client in self.clients:
                            log = str(client.getpeername()) + " disconnected"
                            logger.info(log)
                            self.clients.pop(client)
            elif msg["to"] in self.clients.values():
                client = list(self.clients.keys())[list(self.clients.values()).index(msg["to"])]
                self.send_data(client=client, data=msg)

    def reader(self, clients: list[socket]) -> dict:
        error = None
        msgs = {}
        for client in clients:
            try:
                data = self.get_data(client=client)
                if self.validator.validate_data("action", data):
                    if data["action"] == "msg":
                        self.validator.validate_data("msg", data)
                        data = self.action(client, data)
                        if data is not None:
                            msgs[client] = data
            except (JSONDecodeError, ValidationError) as e:
                error = error_400()
                logger.error(str(e))
            finally:
                if error is not None:
                    try:
                        self.send_data(client=client, data=error)
                        client.close()
                    except ConnectionResetError:
                        if client in self.clients:
                            user = self.clients.pop(client)
                            msg = "Пользователь: '{user}' покинул чат!".format(user=user)
                            msgs[client] = request_msg(sender="server", to="#server",
                                                       encoding=self.encoding, message=msg)
                        logger.info("Потеряно соединение с: {}".format(client.getpeername()))

        return msgs

    def login(self, account: dict, client: socket):
        name = account["account_name"]
        password = account.get("password", None)
        client_id = self.db.Clients.login(name=name)
        contact = self.db.Contacts.get(self.db.Contacts.client_id == client_id)
        if contact is None:
            ip, port = client.getpeername()
            history_id = self.db.History.login(client_id=client_id, ip=ip, port=port, password=password)
            self.db.Contacts.create(client_id=client_id, history_id=history_id)
            return True
        else:
            return False

    def accept(self):
        try:
            client, addr = self.socket.accept()
        except OSError:
            return
        logger.info("Запрос на соединение от: {}".format(addr))
        client.settimeout(self.select_wait)
        try:
            data = self.get_data(client=client)
            client.settimeout(None)
            if self.validator.validate_data("presence", data):
                user = data["user"]["account_name"]
                if user not in self.clients.values():
                    self.clients.setdefault(client, user)
                    self.send_data(client=client, data=ok("Welcome"))
                    self.login(data["user"], client)
                else:
                    self.send_data(client=client, data=error_400(code=409))
                    client.close()
                    logger.error("User: {user}, {error}".format(user=user, error=RESPONSE[409]))
        except OSError:
            return
        except (JSONDecodeError, ValidationError) as e:
            self.send_data(client=client, data=error_400())
            client.close()
            logger.error(str(e))

    def run(self):
        self.init()
        j = self.db.Clients.select()
        while True:
            self.accept()
            read = []
            write = []
            error = []
            try:
                read, write, error = select.select(self.clients.keys(), self.clients.keys(), [], self.select_wait)
            except OSError:
                pass
            msgs = self.reader(read)
            if msgs:
                self.writer(write, msgs)