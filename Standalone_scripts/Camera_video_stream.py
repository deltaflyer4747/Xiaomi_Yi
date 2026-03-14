#! /usr/bin/env python
# encoding: utf-8

import re
import time
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


tosend = '{"msg_id":259,"token":%s,"param":"none_force"}' % token
srv.send(tosend.encode())
srv.recv(512)
print("Live webcam stream is now available.")
print('(Run VLC, select "Media"->"Open network stream" and open')
print('rtsp://%s/live' % camaddr)
print()
print("Press CTRL+C to end this streamer")

try:
    while 1:
        time.sleep(1)
except KeyboardInterrupt:
    srv.close()
