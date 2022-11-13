import logging

from numpy.polynomial import Polynomial as Poly

from .params import *
from .utils import gen_ring_vec, poly_to_bytes, bytes_to_poly


class PubParams:
    def __init__(self):
        self.big_a = [Poly(0) for _ in range(M - 1)]
        self.big_h = [Poly(0) for _ in range(M - 1)]

    def generate(self):
        logging.info('generating pub params ...')
        self.big_a = gen_ring_vec(M - 1)
        self.big_h = gen_ring_vec(M - 1)
        logging.info('done generating pub params ...')

    def to_bytes(self):
        data = bytearray()
        for i in range(M - 1):
            data.extend(poly_to_bytes(self.big_h[i]))
        for i in range(M - 1):
            data.extend(poly_to_bytes(self.big_a[i]))
        return data

    def from_bytes(self, data):
        for i in range(M - 1):
            j = i * POLY_BYTES
            self.big_h[i] = bytes_to_poly(data[j : j + POLY_BYTES])
            self.big_a[i] = bytes_to_poly(
                data[POLY_BYTES * (M - 1) + j : POLY_BYTES * (M - 1) + j + POLY_BYTES]
            )
