import json
import base64
import argparse


def decode_part(part):
    b64decoded = base64.b64decode(part.encode()).decode()
    return json.loads(b64decoded)


def decode_jwt(jwt):
    header, body, _ = jwt.split(".")
    header = decode_part(header)
    body = decode_part(body)
    return (header, body)


def main(args):
    header, body = decode_jwt(args.jwt)
    print("\n***** Results *****")
    print(f"Header:\n{header}")
    print("")
    print(f"Body:\n{body}")


def parser():
    parser = argparse.ArgumentParser(description="Decode JWT")
    parser.add_argument("jwt")
    return parser.parse_args()


if __name__ == "__main__":
    args = parser()
    main(args)
