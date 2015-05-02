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



tosend = '{"msg_id":3,"token":%s}' %token 
srv.send(tosend)

while 1:
	conf = srv.recv(4096)
	if "param" in conf:
		break

conf = conf[37:]

myconf = conf.split(",")

for mytag in myconf:
	print mytag

print "_____________________________________________"
print 
print "press CTRL+C to close"

while 1:
	time.sleep(1)
