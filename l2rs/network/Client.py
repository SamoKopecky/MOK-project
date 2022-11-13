import logging
import socket

from .MsgType import MsgType
from .Role import Role
from .params import *
from .utils import create_data, parse_header
from ..scheme.KeyPair import KeyPair
from ..scheme.PubParams import PubParams
from ..scheme.params import *
from ..scheme.scheme import sign, verify
from ..scheme.utils import bytes_to_poly, poly_to_bytes


class Client:
    def __init__(self, port, bools):
        self.proxy_port = port
        self.proxy_address = "127.0.0.1"
        self.sock = None
        self.pub_params = PubParams()
        self.key_pair = KeyPair()
        self.keys = []
        self.role = Role.role_from_string(bools)

    async def start_client(self):
        # Init
        self.sock = socket.create_connection((self.proxy_address, self.proxy_port))

        # Request public parameters
        self.sock.send(create_data(MsgType.NEED_PUB_PARAMS))
        self.pub_params.from_bytes(self.receive(MsgType.PUB_PARAMS))

        # Generate public key from received public parameters
        self.key_pair.generate(self.pub_params.big_a)

        # Send my public key
        public_key = poly_to_bytes(self.key_pair.public_key)
        self.sock.send(create_data(MsgType.MY_PUB_KEY, public_key))

        if self.role == Role.SIGNER:
            while True:
                message = int(input("Enter a number to sign: "))

                # Receive all public keys
                self.get_public_keys()

                # Chose PI
                pi = 0
                for i in range(len(self.keys)):
                    if self.keys[i] == self.key_pair.public_key:
                        pi = i

                # Generate signature
                signature = sign(
                    pi,
                    message,
                    self.keys,
                    self.pub_params,
                    self.key_pair.private_key,
                    len(self.keys),
                )

                # Send signature
                signature_bytes = bytearray()
                [signature_bytes.extend(poly_to_bytes(poly)) for poly in signature]
                signature_bytes.extend(message.to_bytes(1, BYTEORDER))
                self.sock.send(create_data(MsgType.SIGNATURE, signature_bytes))

                # Verify signature
                signature_bytes = self.receive(MsgType.SIGNATURE)
                logging.info(
                    f"signature verified: {self.verify_signature(signature_bytes)}"
                )
        elif self.role == Role.VERIFIER:
            while True:
                # Verify signature
                signature_bytes = self.receive(MsgType.SIGNATURE)
                self.get_public_keys()
                logging.info(
                    f"signature verified: {self.verify_signature(signature_bytes)}"
                )

    def receive(self, expected_type: MsgType):
        data = bytearray()
        data.extend(self.sock.recv(RECEIVE_LEN))
        msg_type, msg_len, data = parse_header(data)
        logging.info(f"receiving {msg_type.name} with size {msg_len} B")
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

    def get_public_keys(self):
        self.sock.send(create_data(MsgType.NEED_PUB_KEYS))
        data = self.receive(MsgType.PUB_KEYS)
        read = 0
        while read != len(data):
            self.keys.append(bytes_to_poly(data[read : read + POLY_BYTES]))
            read += POLY_BYTES

    def verify_signature(self, data):
        signature = []
        for i in range(0, len(data) - 1, POLY_BYTES):
            signature.append(bytes_to_poly(data[i : i + POLY_BYTES]))
        message = data[-1]
        logging.info(f"Received message: {message}")
        return verify(
            signature,
            message,
            self.keys,
            self.pub_params,
            len(self.keys),
        )
