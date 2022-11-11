import numpy as np
from typing import List
from .KeyPair import KeyPair
from numpy.polynomial import Polynomial as Poly
from .PubParams import PubParams
from .common import (
    ring_vec_ring_vec_mul,
    lift,
    h_one,
    random_ring_vec,
    bytes_to_poly,
    ring_vec_ring_mul,
    ring_sum,
    flatten,
    unflatten,
    poly_to_bytes,
)
from .params import *


def key_gen(pub_params):
    return [KeyPair(pub_params.big_a) for _ in range(W)]


def sign(
    pi: int, message: int, key_pairs: List[KeyPair], pub_params: PubParams
) -> List[Poly]:
    big_s_pi = key_pairs[pi].private_key
    big_s_pi_2q = big_s_pi + [Poly([1 for _ in range(N)])]
    big_l = [pair.public_key for pair in key_pairs]

    h = ring_vec_ring_vec_mul(pub_params.big_h, big_s_pi, Q)

    big_h_2q = lift(pub_params.big_h, h)
    big_a_pi_2q = lift(pub_params.big_a, big_l[pi])

    u = random_ring_vec()

    c = [bytes(0) for _ in range(W)]
    t = [[Poly(0) for _ in range(M)] for _ in range(W)]

    c[(pi + 1) % W] = h_one(
        big_l,
        big_h_2q,
        message,
        ring_vec_ring_vec_mul(big_a_pi_2q, u, Q),
        ring_vec_ring_vec_mul(big_h_2q, u, Q),
    )

    for i in range(pi + 1, pi + W):
        i %= W
        i_plus_one = (i + 1) % W
        big_a_i_2q = lift(pub_params.big_a, big_l[i])
        t[i] = random_ring_vec()
        q_times_ci = bytes_to_poly(c[i]) * Q
        c[i_plus_one] = h_one(
            big_l,
            big_h_2q,
            message,
            ring_sum(q_times_ci, ring_vec_ring_vec_mul(big_a_i_2q, t[i], Q), Q),
            ring_sum(q_times_ci, ring_vec_ring_vec_mul(big_h_2q, t[i], Q), Q),
        )

    b = (-1) ** (np.random.randint(low=0, high=2))
    c_pi = bytes_to_poly(c[pi]) * b
    result = ring_vec_ring_mul(big_s_pi_2q, c_pi, Q)
    for i in range(len(result)):
        result[i] += u[i]
    t[pi] = result
    t = flatten(t)
    return [bytes_to_poly(c[0])] + t + [h]


def verify(
    signature: List[Poly], message: int, key_pairs: List[KeyPair], pub_params: PubParams
) -> bool:
    signed_c1 = signature[0]
    t = unflatten(signature[1 : len(signature) - 1], M)
    h = signature[len(signature) - 1]
    big_l = [pair.public_key for pair in key_pairs]

    big_h_2q = lift(pub_params.big_h, h)
    c = [bytes(0) for _ in range(W)]
    c[0] = poly_to_bytes(signed_c1)

    for i in range(W):
        i %= W
        i_plus_one = (i + 1) % W
        big_a_i_2q = lift(pub_params.big_a, big_l[i])
        q_times_ci = bytes_to_poly(c[i]) * Q
        c[i_plus_one] = h_one(
            big_l,
            big_h_2q,
            message,
            ring_sum(q_times_ci, ring_vec_ring_vec_mul(big_a_i_2q, t[i], Q), Q),
            ring_sum(q_times_ci, ring_vec_ring_vec_mul(big_h_2q, t[i], Q), Q),
        )

    verified_c1 = bytes_to_poly(c[0])
    return verified_c1 == signed_c1
