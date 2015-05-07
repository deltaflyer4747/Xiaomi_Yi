#! /usr/bin/env python
# encoding: windows-1250
#
# Res Andy 

import os, re, time, socket, subprocess, sys, threading, webbrowser
from Tkinter import *
import tkMessageBox

class App:

	def __init__(self, master):
		self.token = ""
		self.connected = False
		self.DonateUrl = "http://sw.deltaflyer.cz/donate.html"
		self.master = master
		self.master.geometry("450x250+300+250")
		self.master.wm_title("Xiaomi Yi C&C by Andy_S")
		
		self.statusBlock = LabelFrame(self.master, bd=1, relief=SUNKEN, text="")
		self.statusBlock.pack(side=BOTTOM, fill=X)
		self.status = Label(self.statusBlock, width=28, text="Disconnected", anchor=W)
		self.status.grid(column=0, row=0)
		self.battery = Label(self.statusBlock, width=12, text="", anchor=W)
		self.battery.grid(column=1, row=0)
		self.usage = Label(self.statusBlock, width=20, text="", anchor=E)
		self.usage.grid(column=2, row=0)

		try: #open the settings file (if exists) and read the settings
			filet = open("settings.cfg","r").read()
			if "\r\n" in filet:
				filek = filet.split("\r\n")
			else:
				filek = filet.split("\n")
			for param in filek:
				if len(param) > 4:
					pname, pvalue = re.findall ("(.+) = (.+)", param)[0]
					if pname == "camaddr":
						self.camaddr = pvalue
					elif pname == "camport":
						self.camport = pvalue 
		except: #no settings file yet, lets create default one & set defaults
			filet = open("settings.cfg","w")
			filet.write('camaddr = 192.168.42.1\r\n') 
			filet.write('camport = 7878\r\n')
			filet.close()
			self.camaddr = "192.168.42.1"
			self.camport = 7878
	
		self.camconn = Frame(self.master) #create connection window with buttons
		b = Button(self.camconn, text="Connect", width=7, command=self.CamConnect)
		b.focus_set()
		b.pack(side=LEFT, padx=2, pady=2)
		self.addrv1 = StringVar()
		self.addrv2 = StringVar()
		e1 = Entry(self.camconn, textvariable=self.addrv1, width=15)
		e2 = Entry(self.camconn, textvariable=self.addrv2, width=6)
		e1.pack(side=LEFT, padx=10)
		e2.pack(side=LEFT, padx=10)
		self.addrv1.set(self.camaddr)
		self.addrv2.set(self.camport)
		self.camconn.pack(side=TOP, fill=X)
		
		
		# create a menu
		self.menu = Menu(self.master)
		root.config(menu=self.menu)
		
		self.Cameramenu = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Camera", menu=self.Cameramenu)
		self.Cameramenu.add_command(label="Format", command=self.ActionFormat, state=DISABLED)
#		self.Cameramenu.add_command(label="Open...", command=self.callback)
		self.Cameramenu.add_separator()
		self.Cameramenu.add_command(label="Exit", command=self.quit)
		
		self.helpmenu = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Help", menu=self.helpmenu)
		
		self.helpmenu.add_command(label="Donate", command=lambda aurl=self.DonateUrl:webbrowser.open_new(aurl))
		self.helpmenu.add_command(label="About...", command=self.AboutProg)
				


	def callback(self):
		print "called the callback!"
	
	def quit(self):
		sys.exit()

	
	def AboutProg(self):
		tkMessageBox.showinfo("About", "Created by Andy_S, 2015\n\nandys@deltaflyer.cz")
	
	def CamConnect(self):
		try:
			self.camaddr = self.addrv1.get() #read IP address from inputbox
			self.camport = int(self.addrv2.get()) #read port from inputbox & convert to integer
			socket.setdefaulttimeout(5)
			self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket
			self.srv.connect((self.camaddr, self.camport)) #open socket
			self.srv.send('{"msg_id":257,"token":0}') #auth to the camera
			data = self.srv.recv(512) #and get a token
			if "rval" in data:
				self.token = re.findall('"param": (.+) }',data)[0]	
			else:
				data = self.srv.recv(512)
				if "rval" in data:
					self.token = re.findall('"param": (.+) }',data)[0]
			if self.token == "": #if we didn't receive a token (we are connecting elsewhere?)
				raise Exception('Connection', 'failed') #throw an exception	
	
			filet = open("settings.cfg","w")
			filet.write('camaddr = %s\r\n' %self.camaddr) 
			filet.write('camport = %s\r\n' %self.camport)
			filet.close()
			self.status.config(text="Connected") #display status message in statusbar
			self.status.update_idletasks()
			self.camconn.destroy() #hide connection selection
			self.Cameramenu.entryconfig(0, state="normal")
			self.connected = True
			self.UpdateUsage()
			self.UpdateBattery()
			self.MainWindow()
		except:
			tkMessageBox.showerror("Connect", "Cannot connect to the address specified")
			self.srv.close()
	

	def UpdateUsage(self):
		tosend = '{"msg_id":5,"token":%s,"type":"total"}' %self.token
		self.srv.send(tosend)
		while 1:
			data = self.srv.recv(512)
			if "param" in data and '"msg_id": 5' in data:
				break
		totalspace = int(re.findall('"param": (.+) }', data)[0])
		tosend = '{"msg_id":5,"token":%s,"type":"free"}' %self.token
		self.srv.send(tosend)
		while 1:
			data = self.srv.recv(512)
			if "param" in data and '"msg_id": 5' in data:
				break
		freespace = float(re.findall('"param": (.+) }', data)[0])
		usedspace = totalspace-freespace
		totalpre = 0
		usedpre = 0
		while 1:
			if usedspace > 1024:
				usedspace = usedspace/float(1024)
				usedpre += 1
			else:
				break
		while 1:
			if totalspace > 1024:
				totalspace = totalspace/float(1024)
				totalpre += 1
			else:
				break
		pres = ["kB", "MB", "GB", "TB"]
		usage = "Used %.1f%s of %.1f%s" %(usedspace, pres[usedpre], totalspace, pres[totalpre])
		self.usage.config(text=usage) #display usage message in statusbar
		self.usage.update_idletasks()
	
	def UpdateBattery(self):
		tosend = '{"msg_id":13,"token":%s}' %self.token
		self.srv.send(tosend)
		while 1:
			data = self.srv.recv(512)
			if "param" in data and '"msg_id":13' in data:
				break
		Ctype, charge = re.findall('"type":"(.+)","param":"(.+)"}', data)[0]
		if Ctype == "adapter":
			Ctype = "Charging"
		else:
			Ctype = "Battery"
		battery = "%s: %s%%" %(Ctype, charge)
		self.battery.config(text=battery) #display usage message in statusbar
		self.battery.update_idletasks()
	
	def MainWindow(self):
		self.mainwindow = Frame(self.master, width=550, height=400)
		self.topbuttons = Frame(self.mainwindow, bg="#aaaaff")
		b = Button(self.topbuttons, text="Control", width=7, command=self.MenuControl)
		b.pack(side=LEFT, padx=10, pady=5)
		b = Button(self.topbuttons, text="Configure", width=7, command=self.MenuConfig, state=DISABLED)
		b.pack(side=LEFT, padx=10, pady=5)
		self.topbuttons.pack(side=TOP, fill=X)
		self.mainwindow.pack(side=TOP, fill=X)
		self.MenuControl()
	
	def MenuControl(self):
		try:
			self.content.destroy()
		except:
			pass
		tosend = '{"msg_id":3,"token":%s}' %self.token 
		self.srv.send(tosend)
		time.sleep(1)
		while 1:
			conf = self.srv.recv(6096)
			if "param" in conf:
				break
		conf = conf[37:]
		self.content = Frame(self.mainwindow)
		self.controlbuttons = Frame(self.content)
		self.bphoto = Button(self.controlbuttons, text="Take a \nPHOTO", width=7, command=self.ActionPhoto, bg="#ccccff")
		self.bphoto.pack(side=LEFT, padx=10, pady=5)
		
		myconf = conf.split(",")
		
		for mytag in myconf:
			if "app_status" in mytag:
				if "record" in mytag:
					self.brecord = Button(self.controlbuttons, text="STOP\nRecording", width=7, command=self.ActionRecordStop, bg="#ff6666")
				else:
					self.brecord = Button(self.controlbuttons, text="START\nRecording", width=7, command=self.ActionRecordStart, bg="#66ff66")
				break
		self.brecord.pack(side=LEFT, padx=10, pady=5)
		for mytag in myconf:
			if "preview_status" in mytag:
				if "off" in mytag:
					self.bstream = Button(self.controlbuttons, text="LIVE\nView", width=7, state=DISABLED)
				else:
					self.bstream = Button(self.controlbuttons, text="LIVE\nView", width=7, command=self.ActionVideoStart, bg="#ffff66")
		self.bstream.pack(side=LEFT, padx=10, pady=5)
		self.controlbuttons.pack(side=TOP, fill=X)
		self.content.pack(side=TOP, fill=X)
	
	def ActionFormat(self):
		if tkMessageBox.askyesno("Format memory card", "Are you sure you want to\nFORMAT MEMORY CARD?\n\nThis action can't be undone\nand will erase ALL DATA!"):
			tosend = '{"msg_id":4,"token":%s}' %self.token
			self.srv.send(tosend)
			self.srv.recv(512)
		self.UpdateUsage()

	def ActionPhoto(self):
		tosend = '{"msg_id":769,"token":%s}' %self.token
		self.srv.send(tosend)
		self.srv.recv(512)
		self.srv.recv(512)
		self.srv.recv(512)
		self.UpdateUsage()

	def ActionRecordStart(self):
		self.UpdateUsage()
		tosend = '{"msg_id":513,"token":%s}' %self.token
		self.srv.send(tosend)
		self.srv.recv(512)
		self.srv.recv(512)
		self.brecord.config(text="STOP\nrecording", command=self.ActionRecordStop, bg="#ff6666") #display status message in statusbar
		self.brecord.update_idletasks()

	def ActionRecordStop(self):
		tosend = '{"msg_id":514,"token":%s}' %self.token
		self.srv.send(tosend)
		self.srv.recv(512)
		self.srv.recv(512)
		self.srv.recv(512)
		self.brecord.config(text="START\nrecording", command=self.ActionRecordStart, bg="#66ff66") #display status message in statusbar
		self.brecord.update_idletasks()
		self.UpdateUsage()
	
	def ActionVideoStart(self):
		tosend = '{"msg_id":259,"token":%s,"param":"none_force"}' %self.token
		self.srv.send(tosend)
		self.srv.recv(512)
		self.srv.recv(512)
		if os.path.isfile("c:/Program Files/VideoLan/VLC/vlc.exe"):
			torun = '"c:/Program Files/VideoLan/VLC/vlc.exe" rtsp://%s:554/live' %(self.camaddr) 
			subprocess.Popen(torun, shell=True)
		else:
			if os.path.isfile("c:/Program Files (x86)/VideoLan/VLC/vlc.exe"):
				torun = '"c:/Program Files (x86)/VideoLan/VLC/vlc.exe" rtsp://%s:554/live' %(self.camaddr)
				subprocess.Popen(torun, shell=True)
			else:
				tkMessageBox.showinfo("Live View", "VLC Player not found\nUse your preferred player to view:\n rtsp://%s:554/live" %(self.camaddr))
	
	def MenuConfig(self):
		try:
			self.content.destroy()
		except:
			pass
		self.content = Frame(self.mainwindow)
		self.controlbuttons = Frame(self.content)
		self.bphoto = Button(self.controlbuttons, text="Nope :-P", width=7, command=self.ActionPhoto)
		self.bphoto.pack(side=LEFT, padx=10, pady=5)
		self.controlbuttons.pack(side=TOP, fill=X)
		self.content.pack(side=TOP, fill=X)
	
	
	
	
root = Tk()
app = App(root)

root.mainloop()

