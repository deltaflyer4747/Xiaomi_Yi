#! /usr/bin/env python
# encoding: windows-1250
#
# Res Andy 

import base64, os, re, socket, subprocess, sys, tempfile, threading, time, webbrowser, zlib
from Tkinter import *
import tkMessageBox

class App:

	def __init__(self, master):
		self.token = ""
		self.connected = False
		self.camconfig = {}
		self.defaultbg = master.cget('bg')
		self.camsettableconfig = {}
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
					elif pname == "custom_vlc_path":
						self.custom_vlc_path = pvalue 
		except: #no settings file yet, lets create default one & set defaults
			filet = open("settings.cfg","w")
			filet.write('camaddr = 192.168.42.1\r\n') 
			filet.write('camport = 7878\r\n')
			filet.write('custom_vlc_path = .\r\n')
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
		self.Cameramenu.add_command(label="Info", command=self.ActionInfo, state=DISABLED)
		self.Cameramenu.add_separator()
		self.Cameramenu.add_command(label="Exit", command=self.quit)
		
		self.helpmenu = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Help", menu=self.helpmenu)
		
		self.helpmenu.add_command(label="Donate", command=lambda aurl=self.DonateUrl:webbrowser.open_new(aurl))
		self.helpmenu.add_command(label="About...", command=self.AboutProg)
				

	def GetAllConfig(self):
		for param in self.camconfig.keys():
			tosend = '{"msg_id":3,"token":%s,"param":"%s"}' %(self.token, param)
			self.srv.send(tosend)
			thisresponse = self.srv.recv(512)
			if '": "settable:' in thisresponse:
				settable, thisoptions = re.findall('": "(.+?):(.+)" } ] }', thisresponse)[0]
				allparams = thisoptions.split("#")
				self.camsettableconfig[param]=allparams


	def ReadConfig(self):
		tosend = '{"msg_id":3,"token":%s}' %self.token 
		self.srv.send(tosend)
		time.sleep(1)
		while 1:
			conf = self.srv.recv(6096)
			if "param" in conf:
				break
		conf = conf[36:]
		myconf = conf.split(",")
		
		for mytag in myconf:
			param, value = re.findall(' { "(.+)": "(.+)" }', mytag)[0]
			self.camconfig[param]=value
			

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
			self.Cameramenu.entryconfig(1, state="normal")
			self.connected = True
			self.ReadConfig()
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
		b = Button(self.topbuttons, text="Configure", width=7, command=self.MenuConfig)
		b.pack(side=LEFT, padx=10, pady=5)
		self.topbuttons.pack(side=TOP, fill=X)
		self.mainwindow.pack(side=TOP, fill=X)
		self.MenuControl()
	
	def MenuControl(self):
		try:
			self.content.destroy()
		except:
			pass
		self.ReadConfig()
		self.content = Frame(self.mainwindow)
		self.controlbuttons = Frame(self.content)
		self.bphoto = Button(self.controlbuttons, text="Take a \nPHOTO", width=7, command=self.ActionPhoto, bg="#ccccff")
		self.bphoto.pack(side=LEFT, padx=10, pady=5)
		
		if "record" in self.camconfig["app_status"]:
			self.brecord = Button(self.controlbuttons, text="STOP\nRecording", width=7, command=self.ActionRecordStop, bg="#ff6666")
		else:
			self.brecord = Button(self.controlbuttons, text="START\nRecording", width=7, command=self.ActionRecordStart, bg="#66ff66")
		self.brecord.pack(side=LEFT, padx=10, pady=5)
		if "off" in self.camconfig["preview_status"]:
			self.bstream = Button(self.controlbuttons, text="LIVE\nView", width=7, state=DISABLED)
		else:
			self.bstream = Button(self.controlbuttons, text="LIVE\nView", width=7, command=self.ActionVideoStart, bg="#ffff66")
		self.bstream.pack(side=LEFT, padx=10, pady=5)
		self.controlbuttons.pack(side=TOP, fill=X)
		self.content.pack(side=TOP, fill=X)
	
	def ActionInfo(self):
		tkMessageBox.showinfo("Camera information", "SW ver: %s\nHW ver: %s\nSN: %s" %(self.camconfig["sw_version"], self.camconfig["hw_version"], self.camconfig["serial_number"]))
		self.UpdateUsage()

	def ActionFormat(self):
		if tkMessageBox.askyesno("Format memory card", "Are you sure you want to\nFORMAT MEMORY CARD?\n\nThis action can't be undone\nALL PHOTOS & VIDEOS WILL BE LOST!"):
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
		self.ReadConfig()

	def ActionRecordStop(self):
		tosend = '{"msg_id":514,"token":%s}' %self.token
		self.srv.send(tosend)
		self.srv.recv(512)
		self.srv.recv(512)
		self.srv.recv(512)
		self.brecord.config(text="START\nrecording", command=self.ActionRecordStart, bg="#66ff66") #display status message in statusbar
		self.brecord.update_idletasks()
		self.ReadConfig()
		self.UpdateUsage()
	
	def ActionVideoStart(self):
		tosend = '{"msg_id":259,"token":%s,"param":"none_force"}' %self.token
		self.srv.send(tosend)
		self.srv.recv(512)
		self.srv.recv(512)
		if self.custom_vlc_path != ".":
			torun = '"%s" rtsp://%s:554/live' %(self.custom_vlc_path, self.camaddr) 
			subprocess.Popen(torun, shell=True)
		else:
			if os.path.isfile("c:/Program Files/VideoLan/VLC/vlc.exe"):
				torun = '"c:/Program Files/VideoLan/VLC/vlc.exe" rtsp://%s:554/live' %(self.camaddr) 
				subprocess.Popen(torun, shell=True)
			else:
				if os.path.isfile("c:/Program Files (x86)/VideoLan/VLC/vlc.exe"):
					torun = '"c:/Program Files (x86)/VideoLan/VLC/vlc.exe" rtsp://%s:554/live' %(self.camaddr)
					subprocess.Popen(torun, shell=True)
				else:
					tkMessageBox.showinfo("Live View", "VLC Player not found\nUse your preferred player to view:\n rtsp://%s:554/live" %(self.camaddr))
	


	def MenuConfig_Apply(self, *args):
		myoption = self.config_thisoption.get()
		myvalue = self.config_thisvalue.get()
		
		if myoption == "camera_clock":
			myvalue = time.strftime("%Y-%m-%d %H:%M:%S")
		tosend = '{"msg_id":2,"token":%s, "type":"%s", "param":"%s"}' %(self.token, myoption, myvalue)
		self.srv.send(tosend)
		self.srv.recv(512)
		self.ReadConfig()

	def MenuConfig_changed(self, *args):
		myoption = self.config_thisoption.get()
		
		self.config_values = self.camsettableconfig[myoption]
		self.config_thisvalue.set(self.camconfig[myoption]) # default value
		if myoption == "video_resolution": #NTSC/PAL resolution check
			self.config_note.config(text='*video_resolution is limited by selected video_standard', bg="#ffff88")
			for checkvalue in self.config_values:
				if self.camconfig["video_standard"] == "NTSC":
					if "24P" in checkvalue or "48P" in checkvalue:
						self.config_values.remove(checkvalue)
				elif self.camconfig["video_standard"] == "PAL":
					if "24P" not in checkvalue or "48P" not in checkvalue:
						self.config_values.remove(checkvalue)
		elif myoption == "video_standard":
			self.config_note.config(text='*video_standard limits video_resolution options', bg="#ffff88")
		elif myoption == "start_wifi_while_booted":
			self.config_note.config(text='*This affects connection by this program', bg="#ffff88")
		elif myoption == "preview_status":
			self.config_note.config(text='*Turn this on to enable LIVE view', bg="#ffff88")
		elif myoption == "camera_clock":
			self.config_note.config(text='*Click Apply to set Camera clock to the same as this PC', bg="#ffff88")
		else:
			self.config_note.config(text='', bg=self.defaultbg)
		menu = self.config_valuebox['menu']
		menu.delete(0, END)
		for value in self.config_values:
			menu.add_command(label=value, command=lambda value=value: self.config_thisvalue.set(value))

	def MenuConfig(self):
		self.ReadConfig()
		self.GetAllConfig()
		try:
			self.content.destroy()
		except:
			pass
		self.content = Frame(self.mainwindow)

		self.controlnote = Frame(self.content, height=20)
		self.config_note = Label(self.controlnote, width=55, text="", anchor=W)
		self.config_note.pack(side=LEFT, fill=X, padx=10)
		self.controlnote.pack(side=TOP, fill=X)
		
		self.controlselect = Frame(self.content)
		self.config_options = sorted(self.camsettableconfig.keys())
		self.config_values = self.camsettableconfig[self.config_options[0]]
		self.config_thisoption = StringVar(self.controlselect)
		self.config_thisoption.trace("w", self.MenuConfig_changed)
		self.config_optionbox = OptionMenu(self.controlselect, self.config_thisoption, *self.config_options)
		self.config_optionbox.config(width=20)
		self.config_optionbox.pack(side=LEFT, padx=10, pady=5)
		self.config_thisvalue = StringVar(self.controlselect)
		self.config_thisvalue.set(self.camconfig[self.config_options[0]]) # default value
		self.config_valuebox = OptionMenu(self.controlselect, self.config_thisvalue, '')
		self.config_thisoption.set(self.config_options[0]) # default value
		self.config_valuebox.config(width=20)
		self.config_valuebox.pack(side=LEFT, padx=10, pady=5)


		self.controlselect.pack(side=TOP, fill=X)

		self.controlbuttons = Frame(self.content)
		self.config_apply = Button(self.controlbuttons, text="Apply", width=7, command=self.MenuConfig_Apply)
		self.config_apply.pack(side=LEFT, padx=10, pady=5)
		self.controlbuttons.pack(side=TOP, fill=X)
		self.content.pack(side=TOP, fill=X)
	
	
	
	
root = Tk()
mysys = os.name
if mysys == "nt":
	ICON = zlib.decompress(base64.b64decode('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'))
	_, ICON_PATH = tempfile.mkstemp()
	with open(ICON_PATH, 'wb') as icon_file:
		icon_file.write(ICON)
	
	root.iconbitmap(default=ICON_PATH)


app = App(root)

root.mainloop()

