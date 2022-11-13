#!/usr/bin/env python3
import asyncio

from L2RS.KeyPair import KeyPair
from L2RS.PubParams import PubParams
from L2RS.scheme import sign, verify
from Client import Client
from Server import Server
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="l2rs",
    )
    role = parser.add_mutually_exclusive_group(required=True)
    action = parser.add_mutually_exclusive_group()
    role.add_argument("-c", "--client", action="store_true", help="run as client")
    role.add_argument(
        "-sp",
        "--server-proxy",
        action="store_true",
        help="run as the server proxy to connect clients",
    )
    action.add_argument(
        "-s",
        "--signer",
        action="store_true",
        help="able to create signatures and send them to everyone",
    )
    action.add_argument(
        "-v", "--verifier", action="store_true", help="only verify received signatures"
    )
    parser.add_argument(
        "-p",
        "--port",
        default=[6000],
        type=int,
        metavar="port",
        help="port to run on, has to be same as the servers/clients",
        nargs="?",
    )
    parsed_args = parser.parse_args(sys.argv[1:])
    if parsed_args.client and (not parsed_args.signer and not parsed_args.verifier):
        parser.error("one of the arguments -s/--signer -v/--verifier is required")
    port = parsed_args.port[0]
    bools = (parsed_args.signer, parsed_args.verifier)

    if parsed_args.server_proxy:
        se = Server(port)
        asyncio.run(se.listen())
        return
    if parsed_args.client:
        cl = Client(port, bools)
        asyncio.run(cl.start_client())
        return


if __name__ == "__main__":
    main()
