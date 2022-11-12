import asyncio
import socket
import threading

from MsgType import MsgType
from Role import Role
from params import *
from utils import create_data, parse_header


class Client:
    def __init__(self, port):
        self.server_port = port
        self.server_addr = "127.0.0.1"
        self.sock = None
        self.loop = None
        self.role = self.parse_role()

    @staticmethod
    def parse_role():
        role = None
        while not role:
            user_input = input("Verifier or signer? (0/1): ")
            try:
                role = Role(int(user_input))
            except Exception as e:
                print(e, "try again")
        return role

    async def start_client(self):
        self.sock = socket.create_connection((self.server_addr, self.server_port))
        self.sock.send(create_data(MsgType.NEED_PUB_PARAMS))
        pub_params = self.receive_data(MsgType.PUB_PARAMS)
        print(f"Pub params: {pub_params}")
        self.sock.send(create_data(MsgType.MY_PUB_KEY, b"my pub key"))
        if self.role == Role.SIGNER:
            while True:
                user_input = input("Create signature? (Y/N):")
                if user_input.upper() == "Y":
                    self.sock.send(create_data(MsgType.NEED_PUB_KEYS))
                else:
                    continue
                data = self.receive_data(MsgType.PUB_KEYS)
                print(f"some data: {data}")
                self.sock.send(create_data(MsgType.SIGNATURE, b"signature"))
                sign = self.receive_data(MsgType.SIGNATURE)
                print(sign)
        elif self.role == Role.VERIFIER:
            while True:
                signature = self.receive_data(MsgType.SIGNATURE)
                print(f"got a signature: {signature}")
                self.sock.send(create_data(MsgType.NEED_PUB_KEYS))
                data = self.receive_data(MsgType.PUB_KEYS)
                print(f"pub keys: {data}")

    def receive_data(self, expected_type: MsgType):
        data = bytearray()
        data.extend(self.sock.recv(RECEIVE_LEN))
        msg_type, msg_len, data = parse_header(data)
        print(f"RECEIVED: {msg_type.name}")
        if msg_type is not expected_type:
            raise "Server error"
        received = len(data)
        while received != msg_len:
            data_chunk = self.sock.recv(RECEIVE_LEN)
            data.extend(data_chunk)
            received += len(data_chunk)
            if not data_chunk or received == msg_len:
                break
        return data

    def receive_signature(self):
        print("started")
        signature = self.receive_data(MsgType.SIGNATURE)
        print(f"got a signature: {signature}")
