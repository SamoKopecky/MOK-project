from common import generate_ring_vec, ring_mul_mod, ring_vec_ring_vec_mul_mod
from params import *


class KeyPair:
    def __init__(self, poly_mod, pub_param_a):
        self.poly_mod = poly_mod
        self.private_key = generate_ring_vec()  # a
        self.public_key = ring_vec_ring_vec_mul_mod(
            pub_param_a, self.private_key, self.poly_mod, Q
        )  # S
