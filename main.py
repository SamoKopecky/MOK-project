import numpy as np
from numpy.polynomial import Polynomial as Poly

from KeyPair import KeyPair
from PubParams import PubParams
from common import (
    ring_vec_ring_vec_mul_mod,
    lift,
    h_one,
    random_byte_vectors,
    convert_bytes_to_poly,
    ring_vec_ring_mul_mod,
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
    c = [0 for _ in range(W)]
    c[(pi + 1) % W] = h_one(
        big_l,
        big_h_2q,
        message,
        ring_vec_ring_vec_mul_mod(big_a_pi_2q, u, poly_mod, Q),
        ring_vec_ring_vec_mul_mod(big_h_2q, u, poly_mod, Q),
    )

    for i in range(pi + 1, pi + W):
        i %= W
        i_plus_one = (i + 1) % W
        print(i, i_plus_one)
        big_a_i_2q = lift(pub_params.big_a, big_l[i])
        t[i] = random_byte_vectors()
        q_times_ci = convert_bytes_to_poly(c[i]) * Q
        first = q_times_ci + ring_vec_ring_vec_mul_mod(big_a_i_2q, t[i], poly_mod, Q)
        second = q_times_ci + ring_vec_ring_vec_mul_mod(big_h_2q, t[i], poly_mod, Q)
        c[i_plus_one] = h_one(big_l, big_h_2q, message, first, second)

    b = (-1) ** (np.random.randint(low=0, high=2))
    c_pi = convert_bytes_to_poly(c[pi]) * b
    result = ring_vec_ring_mul_mod(big_s_pi_2q, c_pi, poly_mod, Q)
    for i in range(len(result)):
        result[i] += u[i]
    t[pi] = result
    return [convert_bytes_to_poly(c[0])] + t + [h]


def verify(poly_mod, signature, message, key_pairs, pub_params) -> bool:
    signed_c1 = signature[0]
    print(signed_c1.coef[:4])
    t = signature[1 : len(signature) - 1]
    h = signature[len(signature) - 1]
    big_l = [pair.public_key for pair in key_pairs]

    big_h_2q = lift(pub_params.big_h, h)
    c = [0 for _ in range(W)]
    c[0] = signed_c1

    for i in range(W):
        i %= W
        i_plus_one = (i + 1) % W
        big_a_i_2q = lift(pub_params.big_a, big_l[i])

        if i == 0:
            q_times_ci = c[i] * Q
        else:
            q_times_ci = convert_bytes_to_poly(c[i]) * Q
        first = q_times_ci + ring_vec_ring_vec_mul_mod(big_a_i_2q, t[i], poly_mod, Q)
        second = q_times_ci + ring_vec_ring_vec_mul_mod(big_h_2q, t[i], poly_mod, Q)
        c[i_plus_one] = h_one(big_l, big_h_2q, message, first, second)

    verified_c1 = convert_bytes_to_poly(c[0])
    for a in c:
        print(convert_bytes_to_poly(a).coef[:4])
    print(verified_c1.coef[:4])
    print(signed_c1.coef[:4])
    return verified_c1 == signed_c1


def main():
    pub_params = PubParams()
    poly_mod = Poly([0 for _ in range(N + 1)])
    poly_mod.coef[0] = 1
    poly_mod.coef[N] = 1
    message = 10
    pi = 1  # Actually pi = 2

    key_pairs = key_gen(poly_mod, pub_params)
    signature = sign(poly_mod, pi, message, key_pairs, pub_params)
    verified = verify(poly_mod, signature, message, key_pairs, pub_params)
    if verified:
        print("###########")
        print("###########")
        print("###########")
        print("###########")
        print("###########")


if __name__ == "__main__":
    main()
