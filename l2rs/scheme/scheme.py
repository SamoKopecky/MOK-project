import logging
from typing import List

import numpy as np
from numpy.polynomial import Polynomial as Poly

from .PubParams import PubParams
from .params import *
from .utils import (
    ring_vec_ring_vec_mul,
    lift,
    h_one,
    random_ring_vec,
    bytes_to_poly,
    ring_vec_ring_mul,
    ring_sum,
    flatten,
    unflatten,
    scalar_vec_mul,
)


def sign(
    pi: int,
    message: bytes,
    big_l: List[Poly],
    pub_params: PubParams,
    private_key: List[Poly],
    w: int,
) -> List[Poly]:
    logging.info("signing ...")
    big_s_pi = private_key
    big_s_pi_2q = big_s_pi + [Poly([1 for _ in range(N)])]

    h = ring_vec_ring_vec_mul(pub_params.big_h, big_s_pi, Q)

    big_h_2q = lift(pub_params.big_h, h)
    big_a_pi_2q = lift(pub_params.big_a, big_l[pi])

    print(ring_vec_ring_vec_mul(big_h_2q, big_s_pi_2q, 2 * Q))

    u = random_ring_vec()

    c = [Poly(0) for _ in range(w)]
    t = [[Poly(0) for _ in range(M)] for _ in range(w)]

    c[(pi + 1) % w] = bytes_to_poly(
        h_one(
            big_l,
            big_h_2q,
            message,
            ring_vec_ring_vec_mul(big_a_pi_2q, u, Q),
            ring_vec_ring_vec_mul(big_h_2q, u, Q),
        )
    )

    for i in range(pi + 1, pi + w):
        i %= w
        i_plus_one = (i + 1) % w
        big_a_i_2q = lift(pub_params.big_a, big_l[i])
        t[i] = random_ring_vec()
        q_times_ci = c[i] * Q
        c[i_plus_one] = bytes_to_poly(
            h_one(
                big_l,
                big_h_2q,
                message,
                ring_sum(q_times_ci, ring_vec_ring_vec_mul(big_a_i_2q, t[i], Q), Q),
                ring_sum(q_times_ci, ring_vec_ring_vec_mul(big_h_2q, t[i], Q), Q),
            )
        )

    b = (-1) ** (np.random.randint(low=0, high=2))
    c_pi = scalar_vec_mul(c[pi], b)
    result = ring_vec_ring_mul(big_s_pi_2q, c_pi, Q)
    for i in range(len(result)):
        result[i] = ring_sum(result[i], u[i], Q)
    t[pi] = result
    t = flatten(t)
    logging.info("done signing ...")
    return [c[0]] + t + [h]


def verify(
    signature: List[Poly],
    message: bytes,
    big_l: List[Poly],
    pub_params: PubParams,
    w: int,
) -> bool:
    logging.info("verifying ...")
    signed_c1 = signature[0]
    t = unflatten(signature[1 : len(signature) - 1], M)
    h = signature[len(signature) - 1]

    big_h_2q = lift(pub_params.big_h, h)
    c = [Poly(0) for _ in range(w)]
    c[0] = signed_c1

    for i in range(w):
        i %= w
        i_plus_one = (i + 1) % w
        big_a_i_2q = lift(pub_params.big_a, big_l[i])
        q_times_ci = c[i] * Q
        c[i_plus_one] = bytes_to_poly(
            h_one(
                big_l,
                big_h_2q,
                message,
                ring_sum(q_times_ci, ring_vec_ring_vec_mul(big_a_i_2q, t[i], Q), Q),
                ring_sum(q_times_ci, ring_vec_ring_vec_mul(big_h_2q, t[i], Q), Q),
            )
        )

    verified_c1 = c[0]
    logging.info("done verifying ...")
    return verified_c1 == signed_c1
