import asyncio
import socket

from MsgType import MsgType
from utils import parse_header, create_data
from params import *


class Server:
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.address = "127.0.0.1"
        self.sock = None
        self.connections = []
        self.pub_keys = []

    async def handle_client(self, client):
        loop = asyncio.get_event_loop()

        while True:
            data = bytearray()
            data.extend(await loop.sock_recv(client, RECEIVE_LEN))
            msg_type, msg_len, data = parse_header(data)
            received = len(data)
            print(f"RECEIVED: {msg_type.name}")
            if msg_type == MsgType.NEED_PUB_PARAMS:
                params = b"abc"*8000
                await loop.sock_sendall(client, create_data(MsgType.PUB_PARAMS, params))
            elif msg_type == MsgType.MY_PUB_KEY:
                data = self.get_rest_of_data(received, msg_len, loop, client, data)
                self.pub_keys.append(data)
                print(f"PUB KEY: {data}")
            elif msg_type == MsgType.NEED_PUB_KEYS:
                pub_keys = bytearray()
                [pub_keys.extend(key) for key in self.pub_keys]
                await loop.sock_sendall(client, create_data(MsgType.PUB_KEYS, pub_keys))
            elif msg_type == MsgType.SIGNATURE:
                for conn in self.connections:
                    await loop.sock_sendall(conn, create_data(MsgType.SIGNATURE, b"this is a signature"))

    def get_rest_of_data(self, received: int, msg_len: int, loop, client, data):
        while received != msg_len:
            data_chunk = loop.sock_recv(client, RECEIVE_LEN)
            data.extend(data_chunk)
            received += len(data_chunk)
            if not data_chunk or received == msg_len:
                break
        return data

    async def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.address, self.port))
        server.listen(8)
        server.setblocking(False)

        loop = asyncio.get_event_loop()

        while True:
            client, addr = await loop.sock_accept(server)
            self.connections.append(client)
            print(f"connection {addr}")
            loop.create_task(self.handle_client(client))
