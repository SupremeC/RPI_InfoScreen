# -*- coding:UTF-8 -*-
#
# | file       :   showStats.py
# | version    :   V1.0
# | date       :   2018-10-01
# | function   :   Show statistics on Waveshare 1.5inch OLED
# |					To preserve OLED screen life the display is turned off unless
# |					motion is detected in the server room. (via MQTT).
# | 				- Listens on MQTT topic
# | 					+ home/basement/serverroom/motionsensor
#
# Requires psUtil.   Install: 	sudo apt-get python-psutil
# Requires pahoMQTT. Install:	sudo apt install python-pip
#								pip install paho-mqtt
#
# INFO:
# Collects various information about the system and displays the info on the screen
#

# RPI
import RPi.GPIO as GPIO
# specific to OLED screen
import DEV_Config
import OLED_Driver






try:
	OLED = OLED_Driver.OLED()
	oled_scan_dir = OLED_Driver.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
	OLED.OLED_Init(oled_scan_dir)
	OLED.OLED_Clear()
	DEV_Config.Driver_Delay_ms(500)

except KeyboardInterrupt:
	logger.info("exiting program")
except:
	logger.error('Exception occurred', exc_info=True)
	raise
finally:
	GPIO.cleanup()  # this ensures a clean exit
