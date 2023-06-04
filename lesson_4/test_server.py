from socket import socket
from unittest import TestCase, main

import sys
import os

basedir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(basedir)

from lesson_3.server import get_socket, preparing_response

class TestServer(TestCase):

    def test_get_socket(self):
        s = get_socket('0.0.0.0', 7777)
        self.assertEqual(type(s), socket)

    def test_preparing_response(self):
        result = preparing_response(response_code=200)
        self.assertEqual(type(result), bytes)


if __name__ == '__main__':
    main()