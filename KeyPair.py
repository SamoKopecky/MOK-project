from common import gen_ring_vec, ring_vec_ring_vec_mul
from params import *


class KeyPair:
    def __init__(self, pub_param_a):
        self.private_key = gen_ring_vec(M - 1)  # a
        self.public_key = ring_vec_ring_vec_mul(
            pub_param_a, self.private_key, Q
        )  # S
