#! /usr/bin/env python
# encoding: utf-8

import re
import socket
from settings import camaddr
from settings import camport


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


tosend = '{"msg_id":514,"token":%s}' % token
srv.send(tosend.encode())
srv.recv(512)
srv.close()
