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


tosend = '{"msg_id":259,"token":%s,"param":"none_force"}' %token
srv.send(tosend)
srv.recv(512)
print "Live webcam stream is now available."
print 'Run VLC, select "Media"->"Open network stream" and open'
print 'rtsp://%s/live' %camaddr
print
print "Press CTRL+C to end this streamer"

while 1:
	time.sleep(1)
