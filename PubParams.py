from common import generate_ring_vec


class PubParams:
    def __init__(self):
        self.big_a = generate_ring_vec()
        self.big_h = generate_ring_vec()
