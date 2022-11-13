from hashlib import shake_256
from typing import List

import numpy as np
from numpy.polynomial import Polynomial as Poly

from .params import *


def gen_ring_vec(vec_size: int) -> List[Poly]:
    vec = []
    gen_range = int(2**GAMMA)
    for i in range(vec_size):
        # Generate a ring
        vec.append(Poly(np.random.randint(low=-gen_range, high=gen_range, size=N)))
        vec[i].coef %= Q
    return vec


def random_ring_vec() -> List[Poly]:
    vec = []
    for i in range(M):
        # Gaussian distribution
        generated = np.random.normal(0, SIGMA, size=N).astype(int)
        generated %= Q
        vec.append(Poly(generated))
    return vec


def ring_sum(a: Poly, b: Poly, mod: int) -> Poly:
    result = Poly([0 for _ in range(N)])
    for i in range(N):
        result.coef[i] = (a.coef[i] + b.coef[i]) % mod
    return result


def ring_mul(a: Poly, b: Poly, mod: int) -> Poly:
    factor = []
    for i in range(N):
        factor.append((a.coef[i] * b.coef[i]) % mod)
    return Poly(factor)


def ring_vec_ring_mul(ring_vec: List[Poly], ring: Poly, mod: int) -> List[Poly]:
    result_ring_vec = []
    for i in range(len(ring_vec)):
        poly_factor = ring_mul(ring_vec[i], ring, mod)
        poly_factor.coef %= mod
        result_ring_vec.append(poly_factor)
    return result_ring_vec


def ring_vec_ring_vec_mul(a: List[Poly], b: List[Poly], mod: int) -> Poly:
    ring = Poly([0 for _ in range(N)])
    for i in range(len(a)):
        poly_factor = ring_mul(a[i], b[i], mod)
        ring = ring_sum(ring, poly_factor, mod)
    return ring


def lift(ring_vec: List[Poly], ring: Poly) -> List[Poly]:
    ring_copy = ring.copy()
    ring_copy = ring_copy * -2
    ring_copy = ring_copy + Q
    ring_copy.coef %= 2 * Q
    ring_vec_copy = ring_vec.copy()
    for i in range(len(ring_vec_copy)):
        ring_vec_copy[i] = ring_vec_copy[i] * 2
        ring_vec_copy[i].coef %= 2 * Q
    return ring_vec_copy + [ring_copy]


def h_one(
    big_l: List[Poly],
    big_h_2q: List[Poly],
    message: bytes,
    first: Poly,
    second: Poly,
) -> bytes:
    shake = shake_256()
    for pub_key in big_l:
        shake.update(pub_key.coef)
    shake.update(message)
    for i in range(M):
        shake.update(big_h_2q[i].coef)
    shake.update(first.coef)
    shake.update(second.coef)
    return shake.digest(int(N * L / 8))


def bytes_to_poly(input_bytes: bytes) -> Poly:
    bits = []
    ring = []
    for i in range(len(input_bytes)):
        bits += [1 if input_bytes[i] & (1 << n) else 0 for n in range(8)]
    for i in range(N):
        ring.append(sum([bits[j + i * L] * (2**j) for j in range(L)]))
    return Poly(ring)


def poly_to_bytes(poly: Poly) -> bytes:
    bits = []
    result_bytes = bytearray(b"")
    for i in range(N):
        bits += [1 if int(poly.coef[i]) & (1 << n) else 0 for n in range(L)]
    for i in range(int(N * L / 8)):
        result_bytes.append(sum([bits[j + i * 8] * (2**j) for j in range(8)]))
    return bytes(result_bytes)


def flatten(array_of_arrays: List[List]) -> List:
    result = []
    for array in array_of_arrays:
        for item in array:
            result.append(item)
    return result


def unflatten(array: List, split_at: int) -> List[List]:
    array_of_arrays = []
    part = []
    for i in range(len(array)):
        part.append(array[i])
        if (i + 1) % split_at == 0:
            array_of_arrays.append(part)
            part = []
    return array_of_arrays
