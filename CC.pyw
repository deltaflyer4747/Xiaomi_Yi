#! /usr/bin/env python
#Â encoding: utf-8
#
# Res andy

AppVersion = "0.4.4"

import base64, json, os, platform, re, select, socket, subprocess, sys, tempfile, threading, time, tkMessageBox, urllib2, webbrowser, zlib
from Tkinter import *
from operator import itemgetter

class App:

	def __init__(self, master):
		self.connected = False
		self.camconfig = {}
		self.ActualAction = ""
		self.defaultbg = master.cget('bg')
		self.camsettableconfig = {}
		self.JsonData = {}
		
		self.DonateUrl = "http://sw.deltaflyer.cz/donate.html"
		self.GitUrl = "https://github.com/deltaflyer4747/Xiaomi_Yi"
		self.UpdateUrl = "https://raw.githubusercontent.com/deltaflyer4747/Xiaomi_Yi/master/version.txt"
		self.ConfigInfo = {"auto_low_light":"Automaticaly increase exposure time in low-light conditions", "auto_power_off":"Power down camera after specified time of inactivity", "burst_capture_number":"Specify ammount of images taken in Burst mode", "buzzer_ring":"Enable/disable camera locator beacon", "buzzer_volume":"Volume of camera beep", "camera_clock":"Click Apply to set Camera clock to the same as this PC", "capture_default_mode":"Mode to enter when changing to Capture via system_default_mode/HW button", "capture_mode":"Changes behavior of \"Photo\" button", "led_mode":"Set preferred LED behavior", "loop_record":"Overwrites oldest files when memory card is full", "meter_mode":"Metering mode for exposure/white ballance", "osd_enable":"Overlay info to hdmi/TV out", "photo_quality":"Set quality of still images", "photo_size":"Set resolution of still images", "photo_stamp":"Overlay date and time of capture to still images", "precise_cont_time":"Delay between individual images in timelapse mode", "precise_selftime":"Set delay to capture in Timer mode", "preview_status":"Turn this on to enable LIVE view", "start_wifi_while_booted":"Enable WiFi on boot", "system_default_mode":"Mode for HW trigger to set when camera is turned on", "system_mode":"Current mode for HW trigger", "video_output_dev_type":"Select video out HDMI or AV out over USB, use same cable as SJ4000", "video_quality":"Set quality of video recordings", "video_rotate":"Rotate video by 180° (upsidedown mount)", "video_resolution":"video_resolution is limited by selected video_standard", "video_stamp":"Overlay date and time to video recordings", "video_standard":"video_standard limits possible video_resolution options", "warp_enable":"On = No fisheye (Compensation ON), Off = Fisheye (Compensation OFF)"}
		self.master = master
		self.master.geometry("445x250+300+250")
		self.master.wm_title("Xiaomi Yi C&C by Andy_S | ver %s" %AppVersion)
		
		self.statusBlock = LabelFrame(self.master, bd=1, relief=SUNKEN, text="")
		self.statusBlock.pack(side=BOTTOM, fill=X)
		self.status = Label(self.statusBlock, width=28, text="Disconnected", anchor=W)
		self.status.grid(column=0, row=0)
		self.battery = Label(self.statusBlock, width=13, text="", anchor=W)
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
					if pname in ("camaddr", "camport", "camwebport", "custom_vlc_path"): setattr(self, pname, pvalue)
			if not {"camaddr", "camport", "camwebport", "custom_vlc_path"} < set(filet.split()): raise
		except Exception: #no settings file yet, lets create default one & set defaults
			filet = open("settings.cfg","w")
			filet.write('camaddr = 192.168.42.1\r\n') 
			filet.write('camport = 7878\r\n')
			filet.write('camwebport = 80\r\n')
			filet.write('custom_vlc_path = .\r\n')
			filet.close()
			self.camaddr = "192.168.42.1"
			self.camport = 7878
			self.camwebport = 80
			self.custom_vlc_path = "."
	
		self.camconn = Frame(self.master) #create connection window with buttons
		b = Button(self.camconn, text="Connect", width=7, command=self.CamConnect)
		b.focus_set()
		b.pack(side=LEFT, padx=10, pady=2)
		self.addrv1 = StringVar()
		self.addrv2 = StringVar()
		self.addrv3 = StringVar()
		l = Label(self.camconn, width=3, text="IP:", anchor=E)
		l.pack(side=LEFT)
		e1 = Entry(self.camconn, textvariable=self.addrv1, width=15)
		e1.pack(side=LEFT)
		l = Label(self.camconn, width=6, text="port:", anchor=E)
		l.pack(side=LEFT)
		e2 = Entry(self.camconn, textvariable=self.addrv2, width=6)
		e2.pack(side=LEFT)
		l = Label(self.camconn, width=10, text="Web port:", anchor=E)
		l.pack(side=LEFT)
		e3 = Entry(self.camconn, textvariable=self.addrv3, width=6)
		e3.pack(side=LEFT)
		self.addrv1.set(self.camaddr)
		self.addrv2.set(self.camport)
		self.addrv3.set(self.camwebport)
		self.camconn.pack(side=TOP, fill=X)
		
		
		# create a menu
		self.menu = Menu(self.master)
		root.config(menu=self.menu)
		
		self.Cameramenu = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Camera", menu=self.Cameramenu, underline=0)
		self.Cameramenu.add_command(label="Info", command=self.ActionInfo, state=DISABLED, underline=0)
		self.Cameramenu.add_command(label="Format", command=self.ActionFormat, state=DISABLED, underline=0)
		self.Cameramenu.add_command(label="Reboot", command=self.ActionReboot, state=DISABLED, underline=0)
		self.Cameramenu.add_command(label="Factory settings", command=self.ActionFactory, state=DISABLED, underline=8)
		self.Cameramenu.add_separator()
		self.Cameramenu.add_command(label="Exit", command=self.quit, underline=1)
		
		self.helpmenu = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Help", menu=self.helpmenu, underline=0)
		
		self.helpmenu.add_command(label="Donate", command=lambda aurl=self.DonateUrl:webbrowser.open_new(aurl), underline=0)
		self.helpmenu.add_command(label="About...", command=self.AboutProg, underline=0)
		self.UpdateCheck()
				

	def UpdateCheck(self):
		try:
			newversion = urllib2.urlopen(self.UpdateUrl).read()
		except Exception:
			newversion = "0"
		if newversion > AppVersion:
			if tkMessageBox.askyesno("New version found", "NEW VERSION FOUND (%s)\nYours is %s\n\nOpen download page?" %(newversion, AppVersion)):
				webbrowser.open_new(self.GitUrl)


	def GetAllConfig(self):
		for param in self.camconfig.keys():
			if param not in ["dev_reboot", "restore_factory_settings", "capture_mode", "wifi_ssid", "wifi_password"]:
				tosend = '{"msg_id":3,"token":%s,"param":"%s"}' %(self.token, param)
				resp = self.Comm(tosend)
				thisresponse = resp["param"][0].values()[0]
				if thisresponse.startswith('settable:'):
					print param
					thisoptions = re.findall('settable:(.+)', thisresponse)[0]
					allparams = thisoptions.replace("\\/","/").split("#")
					self.camsettableconfig[param]=allparams


	def GetDetailConfig(self, param):
		if param not in ["dev_reboot", "restore_factory_settings", "wifi_ssid", "wifi_password"]:
			tosend = '{"msg_id":3,"token":%s,"param":"%s"}' %(self.token, param)
			resp = self.Comm(tosend)
			thisresponse = resp["param"][0].values()[0]
			if thisresponse.startswith('settable:'):
				thisoptions = re.findall('settable:(.+)', thisresponse)[0]
				allparams = thisoptions.replace("\\/","/").split("#")
				self.camsettableconfig[param]=allparams


	def ReadConfig(self):
		tosend = '{"msg_id":3,"token":%s}' %self.token 
		resp = self.Comm(tosend)
		self.camconfig = {}
		for each in resp["param"]: self.camconfig.update(each)
			
	
	def quit(self):
		sys.exit()

	
	def AboutProg(self):
		tkMessageBox.showinfo("About", "Control&Configure | ver. %s\nCreated by Andy_S, 2015\n\nandys@deltaflyer.cz" %AppVersion)
	
	def CamConnect(self):
		try:
			self.camaddr = self.addrv1.get() #read IP address from inputbox
			self.camport = int(self.addrv2.get()) #read port from inputbox & convert to integer
			self.camwebport = int(self.addrv3.get()) #read port from inputbox & convert to integer
			socket.setdefaulttimeout(5)
			self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket
			self.srv.connect((self.camaddr, self.camport)) #open socket
			self.srv.setblocking(0)
			self.connected = True
			self.thread_read = threading.Thread(target=self.JsonReader)
			self.thread_read.setDaemon(True)
			self.thread_read.setName('JsonReader')
			self.thread_read.start()
			self.token = ""
			tokentime = time.time()
			self.srv.send('{"msg_id":257,"token":0}') #auth to the camera
			while self.token == "":
				if time.time()+5>tokentime:
					continue
				else:
					raise Exception('Connection', 'failed') #throw an exception
			filet = open("settings.cfg","w")
			filet.write('camaddr = %s\r\n' %self.camaddr) 
			filet.write('camport = %s\r\n' %self.camport)
			filet.write('camwebport = %s\r\n' %self.camwebport)
			filet.write('custom_vlc_path = %s\r\n' %self.custom_vlc_path)
			filet.close()
			self.status.config(text="Connected") #display status message in statusbar
			self.status.update_idletasks()
			self.camconn.destroy() #hide connection selection
			self.Cameramenu.entryconfig(0, state="normal")
			self.Cameramenu.entryconfig(1, state="normal")
			self.Cameramenu.entryconfig(2, state="normal")
			self.Cameramenu.entryconfig(3, state="normal")
	
	
			self.ReadConfig()
			self.UpdateUsage()
			self.UpdateBattery()
			self.MainWindow()
		except Exception:
			self.connected = False
			tkMessageBox.showerror("Connect", "Cannot connect to the address specified")
			self.srv.close()
	
	def JsonReader(self):
		data = ""
		counter = 0
		flip = 0
		while self.connected:
			try:
				ready = select.select([self.srv], [], [])
				if ready[0]:
					byte = self.srv.recv(1)
					if byte == "{":
						counter += 1
						flip = 1
					elif byte == "}":
						counter -= 1
					data += byte
					
					if flip == 1 and counter == 0:
						try:
							data_dec = json.loads(data)
							data = ""
							flip = 0
							if "msg_id" in data_dec.keys():
								if data_dec["msg_id"] == 257:
									self.token = data_dec["param"]
								self.JsonData[data_dec["msg_id"]] = data_dec
							else:
								raise Exception('Unknown','data')
						except Exception:
							print data
			except Exception:
				self.connected = False

	def Comm(self, tosend):
		Jtosend = json.loads(tosend)
		msgid = Jtosend["msg_id"]
		self.JsonData[msgid] = ""
		self.srv.send(tosend)
		while self.JsonData[msgid]=="":continue
		if self.JsonData[msgid]["rval"] == -4: #wrong token, ackquire new one & resend - "workaround" for camera insisting on tokens
			self.token = ""
			self.srv.send('{"msg_id":257,"token":0}')
			while self.token=="":continue
			Jtosend["token"] = self.token
			tosend = json.dumps(Jtosend)
			self.JsonData[msgid] = ""
			self.srv.send(tosend)
			while self.JsonData[msgid]=="":continue
		return self.JsonData[msgid]

	def UpdateUsage(self):
		tosend = '{"msg_id":5,"token":%s,"type":"total"}' %self.token
		totalspace = self.Comm(tosend)["param"]
		tosend = '{"msg_id":5,"token":%s,"type":"free"}' %self.token
		freespace = float(self.Comm(tosend)["param"])
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
		resp = self.Comm(tosend)
		Ctype = resp["type"]
		charge = resp["param"]

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
		self.MainButtonControl = Button(self.topbuttons, text="Control", width=7, command=self.MenuControl)
		self.MainButtonControl.pack(side=LEFT, padx=10, ipadx=5, pady=5)
		self.MainButtonConfigure = Button(self.topbuttons, text="Configure", width=7, command=self.MenuConfig)
		self.MainButtonConfigure.pack(side=LEFT, padx=10, ipadx=5, pady=5)
		self.MainButtonFiles = Button(self.topbuttons, text="Files", width=7, command=self.FileManager)
		self.MainButtonFiles.pack(side=LEFT, padx=10, ipadx=5, pady=5)
		self.topbuttons.pack(side=TOP, fill=X)
		self.mainwindow.pack(side=TOP, fill=X)
		self.MenuControl()
	
	def MenuControl(self):
		self.ReadConfig()
		try:
			self.content.destroy()
		except Exception:
			pass
		self.content = Frame(self.mainwindow)
		self.controlbuttons = Frame(self.content)
		if self.camconfig["capture_mode"] == "precise quality":
			self.bphoto = Button(self.controlbuttons, text="Take a \nPHOTO", width=13, command=self.ActionPhoto, bg="#ccccff")
		elif self.camconfig["capture_mode"] == "precise quality cont.":
			if self.camconfig["precise_cont_capturing"] == "off":
				self.bphoto = Button(self.controlbuttons, text="Start\nTIMELAPSE", width=13, command=self.ActionPhoto, bg="#66ff66")
			else:
				self.bphoto = Button(self.controlbuttons, text="Stop\nTIMELAPSE", width=13, command=self.ActionPhoto, bg="#ff6666")
		elif self.camconfig["capture_mode"] == "burst quality":
			self.bphoto = Button(self.controlbuttons, text="Burst \nPHOTOS", width=13, command=self.ActionPhoto, bg="#ffccff")
		elif self.camconfig["capture_mode"] == "precise self quality":
			self.bphoto = Button(self.controlbuttons, text="Delayed\nPHOTO", width=13, command=self.ActionPhoto, bg="#ccffff")
		self.bphoto.pack(side=LEFT, padx=12, pady=5)
		
	
		if "record" in self.camconfig["app_status"]:
			self.brecord = Button(self.controlbuttons, text="STOP\nRecording", width=7, command=self.ActionRecordStop, bg="#ff6666")
			self.bphoto.config(state=DISABLED)
			self.bphoto.update_idletasks() 
		else:
			self.brecord = Button(self.controlbuttons, text="START\nRecording", width=7, command=self.ActionRecordStart, bg="#66ff66")
		self.brecord.pack(side=LEFT, padx=10, ipadx=5, pady=5)
		if self.camconfig["capture_mode"] == "precise quality cont.":
			if self.camconfig["precise_cont_capturing"] == "on":
				self.brecord.config(state=DISABLED) 
				self.brecord.update_idletasks()


		if "off" in self.camconfig["preview_status"] or "record" in self.camconfig["app_status"]:
			self.bstream = Button(self.controlbuttons, text="LIVE\nView", width=7, command=self.ActionVideoStart, bg="#ffff66", state=DISABLED)
		else:
			self.bstream = Button(self.controlbuttons, text="LIVE\nView", width=7, command=self.ActionVideoStart, bg="#ffff66")
		self.bstream.pack(side=LEFT, padx=10, ipadx=5, pady=5)
		self.controlbuttons.pack(side=TOP, fill=X)

		self.FramePhotoButtonMod = Frame(self.content)
		self.Photo_options = {"precise quality":"Single","precise quality cont.":"Timelapse","burst quality":"Burst","precise self quality":"Delayed"}
		self.Photo_thisvalue = StringVar(self.FramePhotoButtonMod)
		self.Photo_thisvalue.set(self.Photo_options[self.camconfig["capture_mode"]]) # actual value
		self.Photo_thisvalue.trace("w", self.MenuPhoto_changed)
		self.Photo_valuebox = OptionMenu(self.FramePhotoButtonMod, self.Photo_thisvalue, *self.Photo_options.values())
		self.Photo_valuebox.config(width=10)
		self.Photo_valuebox.pack(side=LEFT, padx=10)
		self.FramePhotoButtonMod.pack(side=TOP, fill=X)


		self.content.pack(side=TOP, fill=X)
	
	def MenuPhoto_changed(self, *args):
		myoption = self.Photo_options.keys()[self.Photo_options.values().index(self.Photo_thisvalue.get())]
		tosend = '{"msg_id":2,"token":%s, "type":"capture_mode", "param":"%s"}' %(self.token, myoption)
		self.Comm(tosend)
		self.MenuControl()

		
	
	def ActionInfo(self):
		tkMessageBox.showinfo("Camera information", "SW ver: %s\nHW ver: %s\nSN: %s" %(self.camconfig["sw_version"], self.camconfig["hw_version"], self.camconfig["serial_number"]))
		self.UpdateUsage()

	def ActionFormat(self):
		if tkMessageBox.askyesno("Format memory card", "Are you sure you want to\nFORMAT MEMORY CARD?\n\nThis action can't be undone\nALL PHOTOS & VIDEOS WILL BE LOST!"):
			tosend = '{"msg_id":4,"token":%s}' %self.token
			self.Comm(tosend)
		self.UpdateUsage()
		if self.ActualAction.startswith("FileManager"):
			self.FileManager()

	def ActionReboot(self):
		if tkMessageBox.askyesno("Reboot camera", "Are you sure you want to\nreboot camera?\n\nThis will close C&C"):
			tosend = '{"msg_id":2,"token":%s, "type":"dev_reboot", "param":"on"}' %self.token
			self.srv.send(tosend)
			time.sleep(1)
			sys.exit()

	def ActionFactory(self):
		if tkMessageBox.askyesno("Reboot camera", "Are you sure you want to\nRESET CAMERA TO FACTORY SETTINGS?\n\nThis will close C&C"):
			tosend = '{"msg_id":2,"token":%s, "type":"restore_factory_settings", "param":"on"}' %self.token
			self.srv.send(tosend)
			time.sleep(1)
			sys.exit()

	def ActionPhoto(self):
		myid = 769
		tosend = '{"msg_id":769,"token":%s}' %self.token
		if self.camconfig["capture_mode"] == "precise quality cont.":
			if self.camconfig["precise_cont_capturing"] == "on":
				tosend = '{"msg_id":770,"token":%s}' %self.token
				myid = 770
		self.Comm(tosend)
		self.ReadConfig()
		self.UpdateUsage()
		if self.camconfig["capture_mode"] == "precise quality cont.":
			if self.camconfig["precise_cont_capturing"] == "off":
				self.bphoto.config(text="Start\nTIMELAPSE", bg="#66ff66")
				self.brecord.config(state="normal") 
			else:
				self.bphoto.config(text="Stop\nTIMELAPSE", bg="#ff6666")
				self.brecord.config(state=DISABLED) 

			self.brecord.update_idletasks()
			self.bphoto.update_idletasks()


	def ActionRecordStart(self):
		self.UpdateUsage()
		tosend = '{"msg_id":513,"token":%s}' %self.token
		self.Comm(tosend)
		self.brecord.config(text="STOP\nrecording", command=self.ActionRecordStop, bg="#ff6666")
		self.brecord.update_idletasks()
		self.bphoto.config(state=DISABLED)
		self.bphoto.update_idletasks() 
		self.ReadConfig()

	def ActionRecordStop(self):
		tosend = '{"msg_id":514,"token":%s}' %self.token
		self.Comm(tosend)
		self.brecord.config(text="START\nrecording", command=self.ActionRecordStart, bg="#66ff66")
		self.brecord.update_idletasks()
		self.bphoto.config(state="normal")
		self.bphoto.update_idletasks() 
		self.ReadConfig()
		self.UpdateUsage()
	
	def ActionVideoStart(self):
		tosend = '{"msg_id":259,"token":%s,"param":"none_force"}' %self.token
		self.Comm(tosend)
		try:
			if self.custom_vlc_path != ".":
				if os.path.isfile(self.custom_vlc_path):
					torun = '"%s" rtsp://%s:554/live' %(self.custom_vlc_path, self.camaddr)
					subprocess.Popen(torun, shell=True)
				else:
					tkMessageBox.showinfo("Live View", "VLC Player not found\nUse your preferred player to view:\n rtsp://%s:554/live" %(self.camaddr))
			else:
				mysys = platform.system()
				if mysys == "Windows":
					if os.path.isfile("c:/Program Files/VideoLan/VLC/vlc.exe"):
						torun = '"c:/Program Files/VideoLan/VLC/vlc.exe" rtsp://%s:554/live' %(self.camaddr) 
						subprocess.Popen(torun, shell=True)
					else:
						if os.path.isfile("c:/Program Files (x86)/VideoLan/VLC/vlc.exe"):
							torun = '"c:/Program Files (x86)/VideoLan/VLC/vlc.exe" rtsp://%s:554/live' %(self.camaddr)
							subprocess.Popen(torun, shell=True)
						else:
							tkMessageBox.showinfo("Live View", "VLC Player not found\nUse your preferred player to view:\n rtsp://%s:554/live" %(self.camaddr))
				elif mysys == "Darwin":
					if os.path.isfile("/Applications/VLC.app/Contents/MacOS/VLC"):
						torun = '"/Applications/VLC.app/Contents/MacOS/VLC" rtsp://%s:554/live' %(self.camaddr)
						subprocess.Popen(torun, shell=True)
					else:
						tkMessageBox.showinfo("Live View", "VLC Player not found\nUse your preferred player to view:\n rtsp://%s:554/live" %(self.camaddr))
				else:
					tkMessageBox.showinfo("Live View", "VLC Player not found\nUse your preferred player to view:\n rtsp://%s:554/live" %(self.camaddr))
		except Exception:
			tkMessageBox.showinfo("Live View", "VLC Player not found\nUse your preferred player to view:\n rtsp://%s:554/live" %(self.camaddr))
	


	def MenuConfig_Apply(self, *args):
		myoption = self.config_thisoption.get()
		myvalue = self.config_thisvalue.get()
		
		if myoption == "camera_clock":
			myvalue = time.strftime("%Y-%m-%d %H:%M:%S")
		tosend = '{"msg_id":2,"token":%s, "type":"%s", "param":"%s"}' %(self.token, myoption, myvalue.replace("/","\\/"))
		self.Comm(tosend)
		if myoption == "video_standard":
			self.GetDetailConfig("video_resolution")
		self.ReadConfig()


	def MenuConfig_changed(self, *args):
		myoption = self.config_thisoption.get()
		
		self.config_values = list(self.camsettableconfig[myoption])
		self.config_thisvalue.set(self.camconfig[myoption].replace("\\/","/")) # default value
		try:
			self.config_note.config(text='*%s' %self.ConfigInfo[myoption], bg="#ffff88")
		except Exception:
			self.config_note.config(text='* Unknown config option, if you know what it does, let me know.', bg=self.defaultbg)
		menu = self.config_valuebox['menu']
		menu.delete(0, END)
		for value in self.config_values:
			menu.add_command(label=value, command=lambda value=value: self.config_thisvalue.set(value))

	def MenuConfig(self):
		self.ReadConfig()
		self.GetAllConfig()
		try:
			self.content.destroy()
		except Exception:
			pass
		self.content = Frame(self.mainwindow)

		self.controlnote = Frame(self.content, height=20)
		self.config_note = Label(self.controlnote, width=63, text="", anchor=W)
		self.config_note.pack(side=LEFT, fill=X, padx=5)
		self.controlnote.pack(side=TOP, fill=X)
		
		self.controlselect = Frame(self.content)
		self.config_options = sorted(self.camsettableconfig.keys())
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
	
	
	def FileYScroll(self, *args):
		apply(self.ListboxFileName.yview, args)
		apply(self.ListboxFileSize.yview, args)
		apply(self.ListboxFileDate.yview, args)

	def FileDownReport(self, bytes_so_far, chunk_size, total_size, FileTP):
		percent = float(bytes_so_far) / total_size
		percent = round(percent*100, 2)
		self.FileProgress.config(text="Downloading %s (%0.2f%%)" %(FileTP, percent), bg=self.defaultbg)

		if bytes_so_far >= total_size:
			self.FileProgress.config(text="%s downloaded" %(FileTP), bg="#ddffdd")

	def FileDownChunk(self, response, chunk_size=8192, report_hook=None, FileTP=""):
		total_size = response.info().getheader('Content-Length').strip()
		total_size = int(total_size)
		bytes_so_far = 0
		
		ThisFileName = "Files/%s" %FileTP
		filek = open(ThisFileName, "wb")
		while 1:
			chunk = response.read(chunk_size)
			bytes_so_far += len(chunk)
			
			if not chunk:
				break
			filek.write(chunk)
			if report_hook:
				self.FileDownReport(bytes_so_far, chunk_size, total_size, FileTP)
		filek.close()

		return bytes_so_far
	

	def FileDownloadThread(self):
		try:
			time.sleep(1)
			FilesToProcess = [self.ListboxFileName.get(idx) for idx in self.ListboxFileName.curselection()]
			FilesToProcessStr = "\n".join(FilesToProcess)
			if not os.path.isdir("Files"):
				os.mkdir("Files",0o777)
			for FileTP in FilesToProcess:
				self.FileProgress.config(text="Downloading", bg=self.defaultbg)
				response = urllib2.urlopen('http://%s:%s/DCIM/%s/%s' %(self.camaddr, self.camwebport, self.MediaDir, FileTP))
				try:
					self.FileDownChunk(response, report_hook=self.FileDownReport, FileTP=FileTP)
				except Exception:
					pass
			self.MainButtonControl.config(state="normal")
			self.MainButtonConfigure.config(state="normal")
			self.MainButtonFiles.config(state="normal")
			self.FileButtonDownload.config(state="normal")
			self.FileButtonDelete.config(state="normal")
			self.Cameramenu.entryconfig(1, state="normal")
			self.Cameramenu.entryconfig(2, state="normal")
			self.Cameramenu.entryconfig(3, state="normal")
							
		except Exception:
			self.FileProgress.config(text="No file selected!", bg="#ffdddd")
			self.MainButtonControl.config(state="normal")
			self.MainButtonConfigure.config(state="normal")
			self.MainButtonFiles.config(state="normal")
			self.FileButtonDownload.config(state="normal")
			self.FileButtonDelete.config(state="normal")
			self.Cameramenu.entryconfig(1, state="normal")
			self.Cameramenu.entryconfig(2, state="normal")
			self.Cameramenu.entryconfig(3, state="normal")
	

	def FileDownload(self, *args):
		self.MainButtonControl.config(state=DISABLED)
		self.MainButtonConfigure.config(state=DISABLED)
		self.MainButtonFiles.config(state=DISABLED)
		self.FileButtonDownload.config(state=DISABLED)
		self.FileButtonDelete.config(state=DISABLED)
		self.Cameramenu.entryconfig(1, state=DISABLED)
		self.Cameramenu.entryconfig(2, state=DISABLED)
		self.Cameramenu.entryconfig(3, state=DISABLED)
		
		self.thread_FileDown = threading.Thread(target=self.FileDownloadThread)
		self.thread_FileDown.start()
					
			
	def FileDelete(self, *args):
		try:
			FilesToProcess = [self.ListboxFileName.get(idx) for idx in self.ListboxFileName.curselection()]
			FilesToProcessStr = "\n".join(FilesToProcess)

			if tkMessageBox.askyesno("Delete file", "Are you sure you want to DELETE\n\n%s\n\nThis action can't be undone!" %FilesToProcessStr):
				tosend = '{"msg_id":1283,"token":%s,"param":"\/var\/www\/DCIM\/%s"}' %(self.token, self.MediaDir) #make sure we are still in the correct path
				self.Comm(tosend)
				for FileTP in FilesToProcess:
					self.FileProgress.config(text="Deleting %s" %FileTP, bg=self.defaultbg)
					tosend = '{"msg_id":1281,"token":%s,"param":"%s"}' %(self.token, FileTP)
					self.Comm(tosend)
					self.FileProgress.config(text="Deleted", bg=self.defaultbg)
		except Exception:
			self.FileProgress.config(text="No file selected!", bg="#ffdddd")
		self.UpdateUsage()
		self.FileManager("Deleted")
	
	def FileManager(self, FileProgressStr="Select a file"):
		self.ActualAction = "FileManager"
		FileListing = {}
		try:
			self.content.destroy()
		except Exception:
			pass
		self.content = Frame(self.mainwindow)
		tosend = '{"msg_id":1283,"token":%s,"param":"\/var\/www\/DCIM"}' %self.token #lets seth initial path in camera
		self.Comm(tosend)
		tosend = '{"msg_id":1282,"token":%s, "param":" -D -S"}' %self.token
		resp = self.Comm(tosend)
		if len(resp["listing"]) > 0:
			self.MediaDir = resp["listing"][0].keys()[0]
			tosend = '{"msg_id":1283,"token":%s,"param":"\/var\/www\/DCIM\/%s"}' %(self.token, self.MediaDir) #lets seth final path in camera
			self.Comm(tosend)
		
			tosend = '{"msg_id":1282,"token":%s, "param":" -D -S"}' %self.token
			for each in self.Comm(tosend)["listing"]: FileListing.update(each)

		if len(FileListing) == 0 :
			self.LabelNoFiles = Label(self.content, width=30, pady=10, text="No files found", bg="#ffcccc")
			self.LabelNoFiles.pack(side=TOP,fill=X)
		else:
			CamFiles=[]
			for filename in FileListing.keys():
				filesize, filedate = re.findall('(.+) bytes\|(.+)',FileListing[filename])[0]
				filesize = float(filesize)
				filepre = 0
				while 1:
					if filesize > 1024:
						filesize = filesize/float(1024)
						filepre += 1
					else:
						break
				CamFiles.append([filename,filesize,filepre,filedate])
			pres = ["B", "kB", "MB", "GB", "TB"]
			self.filelist = Frame(self.content, bg="#ffffff")
			self.LabelFileHead = LabelFrame(self.filelist, bd=1, relief=SUNKEN, text="")
			self.LabelFileHead.pack(side=TOP)
			self.LabelFileName = Label(self.LabelFileHead, width=20, bd=1, relief=RIDGE, text="Filename", anchor=CENTER)
			self.LabelFileName.grid(column=0, row=0)
			self.LabelFileSize = Label(self.LabelFileHead, width=12, bd=1, relief=RIDGE, text="Size", anchor=CENTER)
			self.LabelFileSize.grid(column=1, row=0)
			self.LabelFileDate = Label(self.LabelFileHead, width=30, bd=1, relief=RIDGE, text="DateTime ▼", anchor=CENTER)
			self.LabelFileDate.grid(column=2, row=0)        	

			self.FilesScrollbar = Scrollbar(self.filelist, orient=VERTICAL)
			self.ListboxFileName = Listbox(self.filelist, yscrollcommand=self.FilesScrollbar.set, selectmode=EXTENDED, height=8, width=20, bd=0, bg="#ffffff", fg="#000000", highlightcolor="#ffffff", highlightthickness=0)
			self.ListboxFileSize = Listbox(self.filelist, yscrollcommand=self.FilesScrollbar.set, height=8, width=12, bd=0, bg="#ffffff", fg="#000000", activestyle=NONE, highlightcolor="#ffffff", highlightthickness=0, selectborderwidth=0, selectbackground="#ffffff", selectforeground="#000000")
			self.ListboxFileDate = Listbox(self.filelist, yscrollcommand=self.FilesScrollbar.set, height=8, width=30, bd=0, bg="#ffffff", fg="#000000", activestyle=NONE, highlightcolor="#ffffff", highlightthickness=0, selectborderwidth=0, selectbackground="#ffffff", selectforeground="#000000")
			self.FilesScrollbar.config(command=self.FileYScroll)
			self.FilesScrollbar.pack(side=RIGHT, fill=Y)
			self.ListboxFileName.pack(side=LEFT, padx=15, fill=BOTH, expand=0)
			self.ListboxFileSize.pack(side=LEFT, padx=15, fill=BOTH, expand=0)
			self.ListboxFileDate.pack(side=LEFT, padx=15, fill=BOTH, expand=0)
			for ThisCamFile in sorted(CamFiles, key=itemgetter(3)):
				self.ListboxFileName.insert(END, ThisCamFile[0])
				self.ListboxFileSize.insert(END, " %.1f%s" %(ThisCamFile[1], pres[ThisCamFile[2]]))
				self.ListboxFileDate.insert(END, ThisCamFile[3])
			self.filelist.pack(side=TOP, fill=X)
			self.FileButtonDownload = Button(self.content, text="Download", width=7, command=self.FileDownload)
			self.FileButtonDownload.pack(side=LEFT, padx=10, ipadx=5, pady=5)
			self.FileButtonDelete = Button(self.content, text="DELETE", width=7, bg="#ff6666", command=self.FileDelete)
			self.FileButtonDelete.pack(side=LEFT, padx=10, ipadx=5, pady=5)
			self.FileProgress = Label(self.content, width=40, anchor=W, bd=1, relief=SUNKEN, text=FileProgressStr, bg=self.defaultbg)
			self.FileProgress.pack(side=RIGHT, fill=X, padx=10)
			

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

