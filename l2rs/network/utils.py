from .MsgType import MsgType
from .params import *


def parse_header(data: bytes):
    msg_type = MsgType(int.from_bytes(data[:1], BYTEORDER))
    length = int.from_bytes(data[1:4], BYTEORDER)
    return msg_type, length, data[4:]


def create_data(msg_type: MsgType, data: bytes = b""):
    print(f"SENDING: {msg_type.name}")
    return (
        msg_type.value.to_bytes(TYPE_LEN, BYTEORDER)
        + int.to_bytes(len(data), DATA_LEN_LEN, BYTEORDER)
        + data
    )


def to_int(data: bytearray):
    data = bytes(data)
    return int(data)
