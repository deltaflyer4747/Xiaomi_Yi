#! /usr/bin/env python
# encoding: windows-1250
#
# Res Andy 

import os, re, sys, time, socket


camaddr = "192.168.42.1"
camport = 7878

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.connect((camaddr, camport))

srv.send('{"msg_id":257,"token":0}')

data = srv.recv(512)
if "rval" in data:
	token = re.findall('"param": (.+) }',data)[0]	
data = srv.recv(512)
if "rval" in data:
	token = re.findall('"param": (.+) }',data)[0]	

filek = open("options.txt","r").readlines()

for line in filek:
	if len(line) > 5:
		if not line.startswith("#"):
			tosend = line %token
			srv.send(tosend)
			srv.recv(512)
