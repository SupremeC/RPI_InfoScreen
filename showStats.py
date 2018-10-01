 # -*- coding:UTF-8 -*-
 ##
 # | file       :   showStats.py
 # | version    :   V1.0
 # | date       :   2018-10-01
 # | function   :   Show statistics on Waveshare 1.5inch OLED 
 #					
 #
 # Requires psUtil.
 # Install: sudo apt-get python-psutil
 #
 # INFO:
 # Collects various information about the system and displays the info on the screen
 #




import commands
import os
import psutil
import platform
import datetime
import time
# RPI
import RPi.GPIO as GPIO
# specific to Oled screen
import DEV_Config
import OLED_Driver
import Image
import ImageDraw
import ImageFont
import ImageColor

try:
	def main():
		print "start"
		#input("vad heter du")
		OLED = OLED_Driver.OLED()
		
		# print "************Init OLED************"
		OLED_ScanDir = OLED_Driver.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
		OLED.OLED_Init(OLED_ScanDir)
		OLED.OLED_Clear()
		DEV_Config.Driver_Delay_ms(500)

		# print "*****Setting up display area*****"
		DEV_Config.Driver_Delay_ms(500)
		image = Image.new("L", (OLED.OLED_Dis_Column, OLED.OLED_Dis_Page), 0)# grayscale (luminance)
		draw = ImageDraw.Draw(image)

		# print "get these values only once since they will not change"
		os, name, version, _, _, _ = platform.uname()
		boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
		macadress = getMAC('eth0')
		
		while(1):
			updateDisplay(os, name, version, boot_time, macadress)
			time.sleep(2)

	def updateDisplay(os, name, version, boot_time, macadress):
		#update values every loop
		currenttime = datetime.datetime.now()
		cpupercent = str(psutil.cpu_percent()) + "%"	# first run gives a wrong value due to CPU load while initializing PSUTIL
		cputemp = getCPUtemperature()
		
		#update every hour
		if currenttime.minute % 59:
			uptime = currenttime - boot_time
			ip_adress = commands.getoutput('hostname -I')

		if currenttime.hour % 23:
			#update every day
			fstotal, fsused, fsfree, fspercent = psutil.disk_usage("/")
		
		
		print os, name, version
		print("Local IP adress: " + ip_adress)
		print("MAC: " + macadress)
		print "CPU temp:", cputemp
		print "CPU %:", cpupercent
		print sizeof_fmt(fsused), "of", sizeof_fmt(fstotal), "(", fspercent, "%)"
		print "uptime:", friendlyTimeDelta(boot_time, currenttime)


	# Return friendly TimeDelta string
	# Example: "4 days, 8 hours 2 minutes"
	def friendlyTimeDelta(start, end=datetime.datetime.now()):
		uptime = end - start
		years, reminder = divmod(uptime.total_seconds(), 31556926)
		days, reminder = divmod(reminder, 86400)
		hours, reminder = divmod(reminder, 3600)
		minutes, seconds = divmod(reminder, 60)
		ret = ""
		if years > 1: ret = str(int(years)) + " years, "
		elif years == 1: ret = "1 year, "
		if days > 1: ret += str(int(days)) + " days, "
		elif days == 1: ret += "1 day, "
		if hours > 1: ret += str(int(hours)) + " hours"
		elif hours == 1: ret += str(int(hours)) + " hour"
		if ret == "" and minutes > 0: ret += str(int(minutes)) + " minutes"
		if ret == "" and seconds > 0: ret += str(int(seconds)) + " seconds"
		return ret


	# Return the MAC address of the specified interface
	def getMAC(interface='eth0'):
		try:
			str = open('/sys/class/net/%s/address' %interface).read()
		except:
			str = "00:00:00:00:00:00"
		return str[0:17]


	# return friendly byte size string.
	# Example: 1024 -> 1kiB
	def sizeof_fmt(num, suffix='B'):
		for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
			if abs(num) < 1024.0:
				return "%3.1f%s%s" % (num, unit, suffix)
			num /= 1024.0
		return "%.1f%s%s" % (num, 'Yi', suffix)


	# Return CPU temperature as a character string                                      
	def getCPUtemperature():
		res = os.popen('vcgencmd measure_temp').readline()
		return(res.replace("temp=","").replace("'C\n",""))


	if __name__=="__main__":
		main()

except KeyboardInterrupt:
	print "exiting program"
except:
	print("exception occured")
	raise
finally:  
   GPIO.cleanup() # this ensures a clean exit