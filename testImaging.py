#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import customtypes
import datetime

data = customtypes.SystemInfo()
data.host.boot_time = datetime.datetime.now() - datetime.timedelta(days=45)
data.host.hostname = "rpi_RB-HA-MQTT"
data.host.mac_address = "B8:27:EB:E6:7C:42"
data.host.os = "Linux"
data.host.ip = "192.168.1.244"
data.host.internet = True
data.cpu.load = "23"
data.cpu.temp = "45"
data.fs.total = 59828416000
data.fs.used = 2134100000
data.fs.free = 57694316000
data.fs.percent = "4%"


def get_font_size(font_name, text, max_width):
    font_size = 8
    font = ImageFont.truetype(font_name, font_size)
    while font.getsize(text)[0] < max_width:
        # iterate until the text size is just larger than the criteria
        font_size += 1
        font = ImageFont.truetype(font_name, font_size)
    # step back to be within bounds
    print "computed font-size = " + str(font_size)
    return ImageFont.truetype(font_name, font_size-1)

# TODO - TEST PIXELS - ALL WHITE
# image_testpixels = Image.new("L", (128, 128), 255)  # blank white image
# im.show()

# TODO - LOGO SPLASH SCREEN
fnt = ImageFont.truetype("TerminusTTF-4.46.0.ttf", 16)
fntl = ImageFont.truetype("TerminusTTF-4.46.0.ttf", 22)
fntxl = ImageFont.truetype("TerminusTTF-4.46.0.ttf", 30)

# HOST
image_plash_logo2 = Image.new("L", (128, 128), 0)  # blank black image
drawing = ImageDraw.Draw(image_plash_logo2)
drawing.rectangle([(0, 0), (127, 10)], fill=255, outline=255, width=2)
drawing.rectangle([(0, 10), (127, 40)], fill=None, outline=255, width=2)
header_font = get_font_size(font_name="TerminusTTF-4.46.0.ttf", text=data.host.hostname, max_width=120)
header_start_pos = (128 - header_font.getsize(data.host.hostname)[0]) / 2
drawing.text((header_start_pos, 11), data.host.hostname, font=header_font, fill=255)
drawing.rectangle([(0, 28), (127, 40)], fill=255, outline=255, width=2)
drawing.text((10, 50), "OS:", font=fnt, fill=128)
drawing.text((20, 66), data.host.os, font=fnt, fill=255)
drawing.text((10, 84), "UPTIME:", font=fnt, fill=128)
drawing.text((20, 100), data.host.up_time, font=fnt, fill=255)
# image_plash_logo2.show()

# NETWORK
image_plash_logo3 = Image.new("L", (128, 128), 0)  # blank black image
drawing = ImageDraw.Draw(image_plash_logo3)
drawing.rectangle([(0, 0), (127, 10)], fill=255, outline=255, width=2)
drawing.rectangle([(0, 10), (127, 40)], fill=None, outline=255, width=2)
header_start_pos = (128 - header_font.getsize(data.host.friendly_internet)[0]) / 2
drawing.text((header_start_pos, 11), data.host.friendly_internet, font=header_font, fill=255)
drawing.rectangle([(0, 28), (127, 40)], fill=255, outline=255, width=2)
drawing.text((15, 50), "IP:", font=fnt, fill=128)
drawing.text((5, 66), data.host.ip, font=fnt, fill=255)
drawing.text((15, 84), "MAC:", font=fnt, fill=128)
drawing.text((5, 100), data.host.mac_address, font=fnt, fill=255)
image_plash_logo3.show()


# CPU TEMP, LOAD
image_plash_logo4 = Image.new("L", (128, 128), 0)  # blank black image
drawing = ImageDraw.Draw(image_plash_logo4)
icon = Image.open('temp.bmp', 'r')
icon_w, icon_h = icon.size
h_offset = 0
if icon_h < 128:
    h_offset = (128 - icon_h) / 2
image_plash_logo4.paste(icon, (5, h_offset))
drawing.text((60, 42), data.cpu.temp + " C", font=fntxl, fill=255)
drawing.text((42, 92), "load = " + str(data.cpu.load + "%"), font=fnt, fill=255)
# image_plash_logo4.show()


# DISK
image_plash_logo5 = Image.new("L", (128, 128), 0)  # blank black image
drawing = ImageDraw.Draw(image_plash_logo5)
icon = Image.open('sdcard.bmp', 'r')
icon_h = icon.size[1]
h_offset = 0
if icon_h < 128:
    h_offset = (128 - 10 - icon_h) / 2
image_plash_logo5.paste(icon, (5, h_offset))
drawing.text((70, 45), data.fs.percent, font=fntxl, fill=255)
drawing.text((2, 100), data.fs.friendly_fs_size(), font=fnt, fill=255)
image_plash_logo5.show()


