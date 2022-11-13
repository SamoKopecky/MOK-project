from enum import Enum
from typing import Tuple


class Role(Enum):
    SIGNER = 0
    VERIFIER = 1

    @staticmethod
    def role_from_string(bools: Tuple[bool, bool]):
        switch = {(True, False): Role.SIGNER, (False, True): Role.VERIFIER}
        return switch[bools]
