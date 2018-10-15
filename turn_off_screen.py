# -*- coding:UTF-8 -*-
#
# | file       :   turn_off_screen.py
# | version    :   V1.0
# | date       :   2018-10-01
# | function   :   Clears screen.
#
#
# RPI
import RPi.GPIO as GPIO
# specific to OLD screen
import DEV_Config
import OLED_Driver



OLED = OLED_Driver.OLED()
oled_scan_dir = OLED_Driver.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
OLED.OLED_Init(oled_scan_dir)
OLED.OLED_Clear()
DEV_Config.Driver_Delay_ms(500)

GPIO.cleanup()  # this ensures a clean exit
