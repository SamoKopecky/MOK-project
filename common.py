import numpy as np
from numpy.polynomial import Polynomial as Poly
from numpy.polynomial import polynomial as poly

from params import *


def generate_ring():
    ring = []
    for i in range(M - 1):
        ring.append(Poly(np.random.randint(low=-Q / 2, high=Q / 2, size=N)))
    return ring


def poly_mul_mod(a, b, mod):
    factor = poly.polymul(a.coef, b.coef) % Q
    _, reminder = poly.polydiv(factor, mod.coef)
    return Poly(reminder)


def ring_mul_mod(a, b, mod):
    ring = np.zeros(N)
    for i in range(len(a)):
        poly_factor = poly_mul_mod(a[i], b[i], mod)
        for j in range(N):
            ring[j] += poly_factor.coef[j]
            ring[j] %= Q
    return Poly(ring)
