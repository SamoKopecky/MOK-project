#!/usr/bin/env python3
import argparse
import asyncio
import logging
import sys
from timeit import timeit

from l2rs.network.Client import Client
from l2rs.network.Proxy import Proxy
from l2rs.network.params import *
from l2rs.scheme.KeyPair import KeyPair
from l2rs.scheme.PubParams import PubParams
from l2rs.scheme.params import *
from l2rs.scheme.scheme import sign, verify


def benchmark(participants, iterations):
    setup_code = f"""\
pub_params = PubParams();
pub_params.generate();
message = b"abc";
pi = 1;

W = {participants};
key_pairs = [KeyPair() for _ in range(W)];
[key.generate(pub_params.big_a) for key in key_pairs];
public_keys = [key_pairs[i].public_key for i in range(W)];
signature = sign(pi, message, public_keys, pub_params, key_pairs[pi].private_key, W);
    """
    sign_sum = timeit(
        "sign(pi, message, public_keys, pub_params, key_pairs[pi].private_key, W)",
        number=iterations,
        globals=globals(),
        setup=setup_code,
    )
    verify_sum = timeit(
        "verified = verify(signature, message, public_keys, pub_params, W)",
        number=iterations,
        globals=globals(),
        setup=setup_code,
    )
    print(get_benchmark_result(participants, iterations, sign_sum))
    print(get_benchmark_result(participants, iterations, verify_sum))


def get_benchmark_result(participants, iterations, sum_time):
    sum_text = f"{iterations} sign iterations with {participants} participants took: {sum_time * 1000:.4f} ms"
    avg_text = f"an iteration with {participants} participants took on average: {(sum_time / iterations) * 1000:.4f} ms"
    return sum_text + "\n" + avg_text


def run_single_iteration():
    pub_params = PubParams()
    pub_params.generate()
    message = b"abc"
    pi = 1  # Actually pi = 2

    big_w = 5
    key_pairs = [KeyPair() for _ in range(big_w)]
    [key.generate(pub_params.big_a) for key in key_pairs]
    public_keys = [key_pairs[i].public_key for i in range(big_w)]

    signature = sign(
        pi, message, public_keys, pub_params, key_pairs[pi].private_key, big_w
    )
    verified = verify(signature, message, public_keys, pub_params, big_w)
    print(f"Verified: {verified}")


def start_with_options():
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
    role.add_argument(
        "-pp",
        "--program-parameters",
        action="store_true",
        help="print current parameters",
    )
    role.add_argument(
        "-b",
        "--benchmark",
        type=int,
        metavar="w",
        help="run a benchmark for w participants",
        nargs="?",
    )
    role.add_argument(
        "-jr",
        "--just-run",
        action="store_true",
        help="run a single iteration and print output",
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
        "-i",
        "--iterations",
        type=int,
        default=50,
        metavar="n",
        help="run a benchmark with n iterations (only works for the benchmark functionality)",
        nargs="?",
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
    if parsed_args.client and not parsed_args.signer and not parsed_args.verifier:
        parser.error("one of the arguments -s/--signer -v/--verifier is required")
    if parsed_args.server_proxy and (parsed_args.signer or parsed_args.verifier):
        parser.error(
            "argument -sp/--server-proxy: not allowed with argument -s/--signer or -v/--verifier"
        )
    bools = (parsed_args.signer, parsed_args.verifier)

    if parsed_args.program_parameters:
        print(get_params())
        return
    if parsed_args.server_proxy:
        se = Proxy(parsed_args.port)
        asyncio.run(se.listen())
        return
    if parsed_args.client:
        cl = Client(parsed_args.port, bools)
        asyncio.run(cl.start_client())
        return
    if parsed_args.benchmark:
        benchmark(parsed_args.benchmark, parsed_args.iterations)
        return
    if parsed_args.just_run:
        run_single_iteration()


def get_params():
    return f"""Scheme parameters:
    q: {Q}
    n: {N}
    m: {M}
    sigma: {SIGMA}
    gamma: {GAMMA}
    ring/polynomial coefficient size: {L} B
    ring/polynomial size: {POLY_BYTES} B
Network parameters:
    header size: {HEADER_BYTES} B
    message type size: {TYPE_BYTES} B
    data length size: {DATA_LEN_BYTES} B
    maximum data length: {MAX_DATA_LEN} B
    message length size: {MSG_LEN_BYTES} B
    maximum message size: {MAX_MSG_SIZE} B"""


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


def main():
    start_with_options()


if __name__ == "__main__":
    main()
