import asyncio
import logging
import socket

from .MsgType import MsgType
from .params import *
from .utils import parse_header, create_data
from ..scheme.PubParams import PubParams
from ..scheme.utils import poly_to_bytes, bytes_to_poly


class Proxy:
    def __init__(self, port: int):
        super().__init__()
        self.port = port
        self.address = "127.0.0.1"
        self.connections = []
        self.pub_keys = []
        self.pub_params = PubParams()

    async def handle_client(self, client: socket.socket):
        loop = asyncio.get_event_loop()

        while True:
            # Listen for messages (commands)
            data = bytearray()
            data.extend(await loop.sock_recv(client, RECEIVE_LEN))
            msg_type, msg_len, data = parse_header(data)
            received = len(data)
            logging.info(f"receiving {msg_type.name} with size {msg_len} B")

            if msg_type == MsgType.NEED_PUB_PARAMS:
                # Send public parameters
                await loop.sock_sendall(
                    client, create_data(MsgType.PUB_PARAMS, self.pub_params.to_bytes())
                )
            elif msg_type == MsgType.MY_PUB_KEY:
                # Receive a public key, save it
                data = await self.receive(received, msg_len, loop, client, data)
                self.pub_keys.append(bytes_to_poly(data))
            elif msg_type == MsgType.NEED_PUB_KEYS:
                # Send all gathered public keys
                pub_keys = bytearray()
                [pub_keys.extend(poly_to_bytes(key)) for key in self.pub_keys]
                await loop.sock_sendall(client, create_data(MsgType.PUB_KEYS, pub_keys))
            elif msg_type == MsgType.SIGNATURE:
                # Forwards signature to other clients
                signature = await self.receive(received, msg_len, loop, client, data)
                for conn in self.connections:
                    await loop.sock_sendall(
                        conn, create_data(MsgType.SIGNATURE, signature)
                    )

    async def listen(self):
        self.pub_params.generate()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.address, self.port))
        server.listen(255)
        server.setblocking(False)
        logging.info(f'listening on {(self.address, self.port)}')

        loop = asyncio.get_event_loop()

        while True:
            client, addr = await loop.sock_accept(server)
            self.connections.append(client)
            logging.info(f"connection from {addr}")
            loop.create_task(self.handle_client(client))

    @staticmethod
    async def receive(received: int, msg_len: int, loop, client, data) -> bytes:
        while received != msg_len:
            data_chunk = await loop.sock_recv(client, RECEIVE_LEN)
            data.extend(data_chunk)
            received += len(data_chunk)
            if not data_chunk or received == msg_len:
                break
        return data
