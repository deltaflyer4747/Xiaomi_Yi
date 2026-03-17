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
    """Main function to take a photo."""
    srv, token = connect_and_get_token()
    if not token:
        print("Failed to get token.")
        srv.close()
        return

    try:
        tosend = '{"msg_id":769,"token":%s}' % token
        srv.send(tosend.encode())
        srv.recv(512)
        print("Photo taken.")
    finally:
        srv.close()


if __name__ == "__main__":
    main()
