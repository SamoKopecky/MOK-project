#!/usr/bin/env python3
import argparse
import asyncio
import logging
import sys

from l2rs.network.Client import Client
from l2rs.network.Proxy import Proxy


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="ring_sig", description="learning tool for the l2rs ring signature scheme"
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
        default=6000,
        type=int,
        metavar="port",
        help="port to run on, has to be same as the servers/clients",
        nargs="?",
    )
    parsed_args = parser.parse_args(sys.argv[1:])
    if parsed_args.client and (not parsed_args.signer and not parsed_args.verifier):
        parser.error("one of the arguments -s/--signer -v/--verifier is required")
    bools = (parsed_args.signer, parsed_args.verifier)

    if parsed_args.server_proxy:
        se = Proxy(parsed_args.port)
        asyncio.run(se.listen())
        return
    if parsed_args.client:
        cl = Client(parsed_args.port, bools)
        asyncio.run(cl.start_client())
        return


def setup_logging():
    blue = "\033[1;34m"
    green = "\033[1;33m"
    reset = "\x1b[0m"

    logger = logging.getLogger(__package__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        f"{green}%(asctime)s{reset} {blue}[%(levelname)s]{reset}: %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == "__main__":
    main()
