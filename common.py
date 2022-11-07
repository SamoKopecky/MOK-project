from hashlib import sha256, shake_128
from typing import Callable, Any, List

import numpy as np
from numpy.polynomial import Polynomial as Poly
from numpy.polynomial import polynomial as poly

from params import *


def generate_ring_vec():
    ring = []
    for i in range(M - 1):
        ring.append(Poly(np.random.randint(low=-Q / 2, high=Q / 2, size=N)))
    return ring


def ring_mul_mod(a, b, mod):
    factor = poly.polymul(a.coef, b.coef) % Q
    _, reminder = poly.polydiv(factor, mod.coef)
    return Poly(reminder)


def ring_vec_scalar_vec(ring_vec, scalar):
    ring_vec_copy = ring_vec.copy()
    for i in range(len(ring_vec)):
        ring_vec_copy[i] *= scalar[i]
        ring_vec_copy[i].coef %= 2 * Q
    return ring_vec_copy


def ring_vec_ring_mul_mod(ring_vec, ring, poly_mod, mod):
    result_ring = np.zeros(N)
    for i in range(len(ring_vec)):
        poly_factor = ring_mul_mod(ring_vec[i], ring, poly_mod)
        for j in range(N):
            result_ring[j] += poly_factor.coef[j]
            result_ring[j] %= mod
    return Poly(result_ring)


def ring_vec_ring_vec_mul_mod(a, b, poly_mod, mod):
    result_ring = np.zeros(N)
    for i in range(len(a)):
        poly_factor = ring_mul_mod(a[i], b[i], poly_mod)
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


def transform_ring_vec(
        ring_vec: List[Poly], transform: Callable[[Poly, int], Any], param: int
) -> List[Poly]:
    ring_vec_copy = ring_vec.copy()
    for i in range(len(ring_vec)):
        ring_vec[i] = transform(ring_vec[i], param)
    return ring_vec_copy


def lift(ring_vec: List[Poly], ring: Poly):
    ring_copy = ring.copy()
    ring_copy = scalar_ring_mul(ring_copy, -2)
    ring_copy = scalar_ring_add(ring_copy, Q)
    return [ring_copy] + transform_ring_vec(ring_vec, scalar_ring_mul, 2)


def h_one(
        big_l: List[Poly],
        big_h_2q: List[Poly],
        message: np.ndarray,
        first: Poly,
        second: Poly,
):
    sha = sha256()
    for pub_key in big_l:
        sha.update(pub_key.coef)
    sha.update(message)
    for i in range(M):
        sha.update(big_h_2q[i].coef)
    sha.update(first.coef)
    sha.update(second.coef)
    digest = sha.digest()
    shake = shake_128()
    shake.update(digest)
    return shake.digest(int(N * 14 / 8))


def random_byte_vectors():
    return Poly(np.random.randint(low=0, high=255, size=N))


def convert_bytes_to_poly(input_bytes):
    bits = []
    ring = []
    for i in range(len(input_bytes) * 8):
        bits.append((input_bytes[int(i / 8)] // 2 ** (i % 8)) % 2)
    for i in range(N):
        bitstring = ''
        for j in range(i*14, 14*(i + 1)):
            bitstring += str(bits[j])
        ring.append(int(bitstring, 2) % Q)
    return Poly(ring)
