# About

This is the python implementation of the Lattice-based one-time Linkable Ring Signature (L2RS) scheme. Reference to this scheme can be found here: https://eprint.iacr.org/2018/379. It also includes a tool for sharing and verifying the signature between users on `localhost`.

The applications consists of two parts:
1. Client -- either a verifier or a signer that generates/verifies the signature,
2. Proxy -- a server providing connectivity between clients and generating public parameters.

## How to run

Supports up to 65534 verifying clients, one signer and one proxy.

1. Install required dependencies with:
    ```shell
    pip install -r requirements.txt
    ```
2. Run only one server with:

    ```shell
    ./ring_sig.py -sp
    ```
   
3. Run `n` verifying clients with:

    ```shell
    ./ring_sig.py -c -v
    ```
   
4. Run one signing client with:

    ```shell
    ./ring_sig.py -c -s
    ```
   
5. Optionally you can also choose the port for boothe proxy and clients:

    ```shell
    ./ring_sig.py -p [PORT]
    ```
   

## How to benchmark

The number of benchmark iterations can be chosen with the `-i/--iterations` option. To run the benchmark use `-b/--benchamrk` and supply the number of participants as an argument. See an example bellow for 4 participants and 100 iterations:

```shell
./ring_sig.py -b 4 -i 100
```

### Help

Get help output with:
```shell
./ring_sig.py -h
```

### Info

Get the parameters with:
```shell
./ring_sig.py -i
```


