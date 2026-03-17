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

tosend = '{"msg_id":3,"token":%s}' % token 
srv.send(tosend.encode())

conf = ""
while 1:
	part = srv.recv(4096).decode('utf-8', errors='ignore')
	conf += part
	if "param" in conf:
		break

# Brittle logic preserved from original to skip JSON header
conf = conf[37:]

myconf = conf.split(",")

for mytag in myconf:
	if len(mytag) > 5:
		found = re.findall('{ "(.+)": "', mytag)
		if found:
			paramname = found[0]
			tosend = '{"msg_id":3,"token":%s,"param":"%s"}' % (token, paramname) 
			srv.send(tosend.encode())
			print(srv.recv(8192).decode('utf-8', errors='ignore'))


print("_____________________________________________")
print()
print("press CTRL+C to close")

try:
	while 1:
		time.sleep(1)
except KeyboardInterrupt:
	srv.close()
