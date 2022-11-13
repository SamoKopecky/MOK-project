from enum import Enum


class MsgType(Enum):
    NEED_PUB_PARAMS = 0
    PUB_PARAMS = 1
    MY_PUB_KEY = 2
    NEED_PUB_KEYS = 3
    PUB_KEYS = 4
    SIGNATURE = 5
