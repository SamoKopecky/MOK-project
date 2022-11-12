#!/usr/bin/env python3
import asyncio

from L2RS.PubParams import PubParams
from L2RS.scheme import key_gen, sign, verify
from Client import Client
from Server import Server
import sys


def main():
    pub_params = PubParams()
    message = 10
    pi = 1  # Actually pi = 2
    port = int(sys.argv[1])

    # key_pairs = key_gen(pub_params)
    # signature = sign(pi, message, key_pairs, pub_params)
    # verified = verify(signature, message, key_pairs, pub_params)
    # print(verified)

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
