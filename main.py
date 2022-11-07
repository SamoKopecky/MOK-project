import numpy as np
from numpy.polynomial import Polynomial as Poly

from hashlib import sha256
from KeyPair import KeyPair
from PubParams import PubParams
from common import (
    ring_vec_ring_vec_mul_mod,
    ring_vec_scalar_vec,
    lift,
    h_one,
    random_byte_vectors,
    scalar_ring_mul,
    convert_bytes_to_poly, ring_vec_ring_mul_mod,
)
from params import *


def key_gen(poly_mod, pub_params):
    return [KeyPair(poly_mod, pub_params.big_a) for _ in range(W)]


def sign(poly_mod, pi, message, key_pairs, pub_params):
    big_s_pi = key_pairs[pi].private_key
    big_s_pi_2q = big_s_pi + [Poly([1 for _ in range(N)])]
    big_l = [pair.public_key for pair in key_pairs]

    h = ring_vec_ring_vec_mul_mod(pub_params.big_h, big_s_pi, poly_mod, Q)

    big_h_2q = lift(pub_params.big_h, h)
    big_a_pi_2q = lift(pub_params.big_a, key_pairs[pi].public_key)
    u = random_byte_vectors()

    t = [0 for _ in range(W)]
    c = [[Poly([0])] for _ in range(W)]
    c[pi + 1] = h_one(
        big_l,
        big_h_2q,
        message,
        ring_vec_ring_mul_mod(big_a_pi_2q, u, poly_mod, 2 * Q),
        ring_vec_ring_mul_mod(big_h_2q, u, poly_mod, 2 * Q),
    )

    for i in range(pi + 1, pi + W):
        i %= W
        i_plus_one = (i + 1) % W
        big_a_i_2q = lift(pub_params.big_a, big_l[i])
        t[i] = random_byte_vectors()
        q_times_ci = convert_bytes_to_poly(c[i]) * Q
        first = q_times_ci + ring_vec_ring_mul_mod(
            big_a_i_2q, t[i], poly_mod, 2 * Q
        )
        second = q_times_ci + ring_vec_ring_mul_mod(big_h_2q, t[i], poly_mod, 2 * Q)
        c[i_plus_one] = h_one(big_l, big_h_2q, message, first, second)

    # TODO: fix this, always get -1
    b = -1 ** (np.random.randint(low=0, high=2, size=1)[0])
    c_pi = convert_bytes_to_poly(c[pi]) * b
    t[pi] = ring_vec_ring_mul_mod(big_s_pi_2q, c_pi, poly_mod, Q) + u
    return [convert_bytes_to_poly(c[1])] + t + [h]


def main():
    pub_params = PubParams()
    poly_mod = Poly([0 for _ in range(N + 1)])
    poly_mod.coef[0] = 1
    poly_mod.coef[N] = 1
    message = np.random.randint(low=0, high=255, size=255)
    pi = 1  # Actually pi = 2

    key_pairs = key_gen(poly_mod, pub_params)
    signature = sign(poly_mod, pi, message, key_pairs, pub_params)
    print()


if __name__ == "__main__":
    main()
