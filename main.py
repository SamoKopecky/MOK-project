#!/usr/bin/env python3
import asyncio

from L2RS.KeyPair import KeyPair
from L2RS.PubParams import PubParams
from L2RS.scheme import sign, verify
from Client import Client
from Server import Server
import sys


def main():
    # pub_params = PubParams()
    # pub_params.generate()
    # message = 10
    # pi = 1  # Actually pi = 2
    #
    # W = 4
    # key_pairs_2 = [KeyPair() for _ in range(W)]
    # [key.generate(pub_params.big_a) for key in key_pairs_2]
    # key_pairs = [key_pairs_2[i].public_key for i in range(W)]
    # signature = sign(pi, message, key_pairs, pub_params, key_pairs_2[pi].private_key, W)
    # verified = verify(signature, message, key_pairs, pub_params, W)
    # print(verified)

    port = int(sys.argv[1])

    if "-s" in sys.argv:
        se = Server(port)
        asyncio.run(se.listen())
        return
    if "-c" in sys.argv:
        cl = Client(port)
        asyncio.run(cl.start_client())
        return


if __name__ == "__main__":
    main()
