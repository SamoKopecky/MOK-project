from numpy.polynomial import Polynomial as Poly

from KeyPair import KeyPair
from common import generate_ring, ring_mul_mod
from params import *


def main():
    poly_mod = Poly([0 for _ in range(N + 1)])
    poly_mod.coef[0] = 1
    poly_mod.coef[N] = 1
    pub_param_a = generate_ring()  # A
    pub_param_h = generate_ring()  # H

    
    pair = KeyPair(poly_mod)
    pair.key_gen(pub_param_a)
    print()


if __name__ == "__main__":
    main()
