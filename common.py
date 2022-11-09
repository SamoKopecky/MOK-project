from hashlib import shake_256
from typing import Callable, Any, List

import numpy as np
from numpy.polynomial import Polynomial as Poly
from numpy.polynomial import polynomial as poly

from params import *


def generate_ring_vec():
    ring = []
    for i in range(M - 1):
        ring.append(Poly(np.random.randint(low=-12418, high=12418, size=N)))
    return ring


def ring_mul(a, b, mod):
    factor = Poly([0 for _ in range(N)])
    for i in range(N):
        factor.coef[i] = (a.coef[i] * b.coef[i]) % mod
    return factor


def ring_vec_ring_mul_mod(ring_vec, ring, mod):
    result_ring = []
    for i in range(len(ring_vec)):
        poly_factor = ring_mul(ring_vec[i], ring, mod)
        poly_factor.coef %= mod
        result_ring.append(poly_factor)
    return result_ring


def ring_vec_ring_vec_mul_mod(a, b, mod):
    result_ring = np.zeros(N)
    for i in range(len(a)):
        poly_factor = ring_mul(a[i], b[i], mod)
        for j in range(N):
            result_ring[j] += poly_factor.coef[j]
            result_ring[j] %= mod
    return Poly(result_ring)


def scalar_ring_mul(ring, scalar):
    ring_copy = ring.copy()
    for i in range(N):
        ring_copy.coef[i] *= scalar
    return ring_copy


def scalar_ring_add(ring, scalar):
    ring_copy = ring.copy()
    for i in range(N):
        ring_copy.coef[i] += scalar
    return ring_copy


def lift(ring_vec: List[Poly], ring: Poly):
    ring_copy = ring.copy()
    ring_copy = scalar_ring_mul(ring_copy, -2)
    ring_copy = scalar_ring_add(ring_copy, Q)
    ring_copy.coef %= 2 * Q
    ring_vec_copy = ring_vec.copy()
    for i in range(len(ring_vec_copy)):
        ring_vec_copy[i] = scalar_ring_mul(ring_vec_copy[i], 2)
        ring_vec_copy[i].coef %= 2 * Q
    return ring_vec_copy + [ring_copy]


def h_one(
        big_l: List[Poly],
        big_h_2q: List[Poly],
        message: int,
        first: Poly,
        second: Poly,
):
    shake = shake_256()
    for pub_key in big_l:
        shake.update(pub_key.coef)
    shake.update(bytes(message))
    for i in range(M):
        shake.update(big_h_2q[i].coef)
    shake.update(first.coef)
    shake.update(second.coef)
    return shake.digest(int(N * 14 / 8))


def random_byte_vectors():
    vectors = []
    for i in range(M):
        generated = np.random.normal(0, SIGMA, size=N)
        for j in range(len(generated)):
            generated[j] = int(generated[j])
        vectors.append(Poly(generated))
    return vectors


def convert_bytes_to_poly(input_bytes):
    bits = []
    ring = []
    for i in range(len(input_bytes) * 8):
        bits.append((input_bytes[int(i / 8)] // 2 ** (i % 8)) % 2)
    for i in range(N):
        bitstring = ""
        for j in range(i * 14, 14 * (i + 1)):
            bitstring += str(bits[j])
        ring.append(int(bitstring, 2) % Q)
    return Poly(ring)
