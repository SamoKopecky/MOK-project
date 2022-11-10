from params import *
from common import gen_ring_vec


class PubParams:
    def __init__(self):
        self.big_a = gen_ring_vec(M - 1)
        self.big_h = gen_ring_vec(M - 1)
