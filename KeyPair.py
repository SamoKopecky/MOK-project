from common import generate_ring_vec, ring_vec_ring_vec_mul_mod
from params import *


class KeyPair:
    def __init__(self, pub_param_a):
        self.private_key = generate_ring_vec()  # a
        self.public_key = ring_vec_ring_vec_mul_mod(
            pub_param_a, self.private_key, Q
        )  # S
