import logging

from numpy.polynomial import Polynomial as Poly

from .params import *
from .utils import gen_ring_vec, ring_vec_ring_vec_mul


class KeyPair:
    def __init__(self):
        self.private_key = Poly(0)
        self.public_key = []

    def generate(self, pub_param_a):
        logging.info("generating key pair ...")
        self.private_key = gen_ring_vec(M - 1)  # a
        self.public_key = ring_vec_ring_vec_mul(pub_param_a, self.private_key, Q)  # S
        logging.info("done generating key pair ...")
