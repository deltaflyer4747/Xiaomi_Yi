#! /usr/bin/env python
# encoding: windows-1250
#
# Res Andy 

import os, re, sys, time, socket
from settings import camaddr
from settings import camport

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.connect((camaddr, camport))

srv.send('{"msg_id":257,"token":0}')

data = srv.recv(512)
if "rval" in data:
	token = re.findall('"param": (.+) }',data)[0]	
else:
	data = srv.recv(512)
	if "rval" in data:
		token = re.findall('"param": (.+) }',data)[0]	

filet = open("options.txt","r").read()
if "\r\n" in filet:
	filek = filet.split("\r\n")
else:
	filek = filet.split("\n")

for line in filek:
	if len(line) > 5:
		if not line.startswith("#"):
			tosend = line %token
#			print tosend
			srv.send(tosend)
			srv.recv(512)
#			print srv.recv(512)
#			print
