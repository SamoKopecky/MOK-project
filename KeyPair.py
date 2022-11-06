from common import generate_ring, poly_mul_mod, ring_mul_mod
from params import *


class KeyPair:
    def __init__(self, poly_mod):
        self.public_key = []  # a
        self.private_key = []  # S
        self.poly_mod = poly_mod

    def key_gen(self, pub_param_a):
        self.private_key = generate_ring()
        self.public_key = ring_mul_mod(pub_param_a, self.private_key, self.poly_mod)
