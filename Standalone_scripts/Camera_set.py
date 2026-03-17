#! /usr/bin/env python
# encoding: utf-8

import re
import socket
from settings import camaddr
from settings import camport


def connect_and_get_token():
    """Establishes a connection and retrieves a token from the camera."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.connect((camaddr, camport))
    srv.send(b'{"msg_id":257,"token":0}')
    token = 0
    data = srv.recv(512).decode('utf-8', errors='ignore')
    if "rval" in data:
        found = re.findall('"param": (.+) }', data)
        if found:
            token = found[0]
    else:
        data = srv.recv(512).decode('utf-8', errors='ignore')
        if "rval" in data:
            found = re.findall('"param": (.+) }', data)
            if found:
                token = found[0]
    return srv, token


def main():
    """Main function to set camera options from a file."""
    srv, token = connect_and_get_token()
    if not token:
        print("Failed to get token.")
        srv.close()
        return

    try:
        with open("options.txt", "r") as f:
            for line in f:
                line = line.strip()
                if len(line) > 5 and not line.startswith("#"):
                    tosend = line % token
                    # print(tosend)
                    srv.send(tosend.encode())
                    srv.recv(512)
                    # print(srv.recv(512))
                    # print()
    except FileNotFoundError:
        print("Error: options.txt not found.")
    finally:
        srv.close()


if __name__ == "__main__":
    main()
