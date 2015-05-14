# Xiaomi_Yi
## Xiaomi Yi Camera Control&Configure GUI and via python scripts

### Multiplatform, runs on Windows, Linux and Mac!

#### Control (Photo, Record, Live View), Configure & Manage files via PC & Wifi.

### CC.exe is compiled - NO PYTHON INSTALLATION NEEDED
#### CC.pyw - for all systems capable of running python with Tkinter


-------
##### Obsolete

For these scripts you need Python 2.7.x https://www.python.org/downloads/ 

Windows Notepad is derping about newline style, use something better than that, like Notepad++, PsPad, or even WordPad

Edit settings.py with your camera IP. No need to launch this script

* Edit options.txt (un/comment lines as needed) and launch Camera_set.py to set uncommented options
* Camera_all_options.py displays all possible options for all possible variables
* Camera_get.py displays current settings from camera
* Camera_photo.py captures single photo
* Camera_record_start.py & Camera_record_stop.py starts / stops video recording respectively
* Camera_video_stream.py enables streaming for RTSP capable player (for example VLC)
