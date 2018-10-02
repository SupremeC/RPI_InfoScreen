 # -*- coding:UTF-8 -*-
 #
 # | file       :   showStats.py
 # | version    :   V1.0
 # | date       :   2018-10-01
 # | function   :   Show statistics on Waveshare 1.5inch OLED
 # | 				- Listens on MQTT topic
 # | 					+ home/basement/serverroom/motionsensor
 # | 				- Publishes MQTT topics
 # | 					+ home/basement/serverroom/rpiA/cputemp
 # | 					+ home/basement/serverroom/rpiA/cpuload
 # | 					+ home/basement/serverroom/rpiA/alive
 # | 					+ home/basement/serverroom/rpiA/diskusage
 #					
 #
 # Requires psUtil.   Install: 	sudo apt-get python-psutil
 # Requires pahoMQTT. Install:	sudo apt install python-pip
 #								pip install paho-mqtt
 #
 # INFO:
 # Collects various information about the system and displays the info on the screen
 #




# Logging
import logging
import logging.config
import commands
import os
import psutil
import platform
import datetime
import time
# MQTT
import paho.mqtt.client as paho
# RPI
import RPi.GPIO as GPIO
# specific to OLED screen
import DEV_Config
import OLED_Driver
import Image
import ImageDraw
import ImageFont
import ImageColor



# Global
LOGGING_CONFIG_FILE = "logging_config.ini"
mqttclient = None
OLED = None
showOnScreen = None
MQTT_SUBSCRIBE_TOPIC = "home/basement/serverroom/motionsensor"



# Logging setup
logging.config.fileConfig(fname=LOGGING_CONFIG_FILE, disable_existing_loggers=True)
logger = logging.getLogger()


try:
	def main():
		logging.addLevelName(100, 'START')
		logging.log(100, "============================")
		logging.log(100, "STARTING UP")
		
		
		logger.info("Initilize OLED screen")
		global OLED
		global showOnScreen
		showOnScreen = False
		OLED = OLED_Driver.OLED()
		OLED_ScanDir = OLED_Driver.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
		OLED.OLED_Init(OLED_ScanDir)
		OLED.OLED_Clear()
		DEV_Config.Driver_Delay_ms(500)

		global mqttclient
		mqttclient = paho.Client(client_id="RPI-A_OLEDScreen", clean_session=False, userdata=None)
		mqttclient.enable_logger(logger)
		mqttclient.on_connect = on_connect
		mqttclient.on_subscribe = on_subscribe
		mqttclient.on_message = on_message
		mqttclient.connect("192.168.1.170", 1883, 60)
		mqttclient.loop_start()

		logger.info("Setting up OLED display area")
		DEV_Config.Driver_Delay_ms(500)
		image = Image.new("L", (OLED.OLED_Dis_Column, OLED.OLED_Dis_Page), 0)# grayscale (luminance)
		draw = ImageDraw.Draw(image)

		logger.info("Fetch platform info once@startup")
		os, name, version, _, _, _ = platform.uname()
		boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
		macadress = getMAC('eth0')
		logging.log(100, "OS: " + os)
		logging.log(100, "Device name: " + name)
		logging.log(100, "version: " + version)
		logging.log(100, "Logging config file: " + LOGGING_CONFIG_FILE)
		logging.log(100, "============================")
		
		
		while(1):
			updateDisplay(os, name, version, boot_time, macadress, showOnScreen)
			time.sleep(2) # seconds


	def on_connect(client, userdata, flags, rc):
		logger.info("CONNACK received with code %d." % (rc))
		client.subscribe(MQTT_SUBSCRIBE_TOPIC, qos=1)
	def on_subscribe(client, userdata, mid, granted_qos):
		logger.info("Subscribed: "+str(mid)+" "+str(granted_qos))
	def on_message(client, userdata, msg):
		global showOnScreen
		logger.info(msg.topic+" "+str(msg.qos)+" "+str(msg.payload)) 
		if msg.topic == MQTT_SUBSCRIBE_TOPIC and msg.payload=="motion":
			showOnScreen = True
		else:
			showOnScreen = False


	def updateDisplay(os, name, version, boot_time, macadress, showOnScreen):
		if showOnScreen == False:
			return
		else:
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
			logger.info("Done updating OLED screen")




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
	logger.info("exiting program")
except:
	logger.error('Exception occurred', exc_info=True)
	raise
finally:  
   GPIO.cleanup() # this ensures a clean exit
   mqttclient.loop_stop()