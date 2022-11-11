from L2RS.PubParams import PubParams
from L2RS.scheme import key_gen, sign, verify


def main():
    pub_params = PubParams()
    message = 10
    pi = 1  # Actually pi = 2

    key_pairs = key_gen(pub_params)
    signature = sign(pi, message, key_pairs, pub_params)
    verified = verify(signature, message, key_pairs, pub_params)
    print(verified)


if __name__ == "__main__":
    main()
