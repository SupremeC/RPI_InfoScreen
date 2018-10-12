#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import logging
import DEV_Config
import OLED_Driver
import time
import threading
import RPi.GPIO as GPIO
logger = logging.getLogger(__name__)


class OledManager(object):
    def __init__(self, splash_duration=5, splash_images=None):
        # type: (int, list) -> object
        """
        OlED display module that allows you to show system information on the screen.
        Call Update() with a parameter of type [customtypes].SystemInfo
        :param splash_duration: total time to show Splash images at startup
        :param splash_images: Image names in a list. Must be mode=gray scale and exactly of size=128x128px
        """
        logger.debug("OLEDManager starting...")
        self._data = None
        self._activate_screen = False
        self.splash_logos = splash_images  # MUST BE mode=gray_scale, size=128x1218px
        self.splash_duration = splash_duration  # seconds
        self.font_std = ImageFont.load("fonts/courB10.pil")
        self.font_h1 = ImageFont.load("fonts/courB18.pil")
        self.font_xl = ImageFont.load("fonts/courB24.pil")
        self.img_host = None  # pre-rendered images
        self.img_network = None
        self.img_cpu = None
        self.img_disk = None
        self._OLED_ScanDir = OLED_Driver.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
        self.OLED = OLED_Driver.OLED()
        self.OLED.OLED_Init(self._OLED_ScanDir)
        time.sleep(0.5)
        self._display_event = threading.Event()
        self._thread = threading.Thread(target=self._internal_thread_loop)  # , args=[False])
        self._thread.name = "oled_internal_thread"
        self._thread.do_run = True
        self._thread.start()
        logger.info("OLEDManager init complete")

    def _internal_thread_loop(self):
            logger.debug("entering OLED _internal_thread_loop")
            assert threading.current_thread().name == "oled_internal_thread"
            if len(self.splash_logos) > 0:
                self.show_splash()
            while self._thread.do_run:
                logger.debug("loop: self._activate_screen = " + str(self._activate_screen))
                while not self._activate_screen:
                    logger.debug("entering wait()...")
                    self.clear_oled()
                    self._display_event.wait()  # sleeps while waiting for event
                    if not self._thread.do_run:
                        self.clear_oled()
                        return
                    self.show_splash()
                    logger.debug("leaving wait()!!!!")
                self._show_system_info()

    def _internal_thread_stop(self):
        if self._thread is not None and self._thread.is_alive():
            logger.debug("stopping OLED screen background thread...")
            self._activate_screen = True  # needed for thread to exit inner WHILE loop
            self._thread.do_run = False
            self._display_event.set()  # wake thread so we can kill it :)
            logger.debug("waiting for thread.join()")
            self._thread.join()
            self._thread = None
        else:
            logger.debug("thread is already dead")

    def update(self, values):
        """
        Async display of data supplied in [values].
        Call off() method to stop.
        :param values: [customTypes.py].[SystemInfo]
        :return: None
        """
        self._data = values
        self._activate_screen = True
        self._display_event.set()  # Tell internal thread that it should wake up

    def _show_system_info(self):
        logger.debug("entering Show_system_info()")
        if self._activate_screen and self._data is not None:
            self.OLED.OLED_ShowImage(self.get_host_image(), 0, 0)
            time.sleep(2.5)
            self.OLED.OLED_ShowImage(self.get_network_image(), 0, 0)
            time.sleep(2.9)
            self.OLED.OLED_ShowImage(self.get_cpu_image(), 0, 0)
            time.sleep(2.3)
            self.OLED.OLED_ShowImage(self.get_disk_image(), 0, 0)
            time.sleep(2.3)

    def show_splash(self, images=None):
        """
        Shows selected images on the screen. Blocking.
        This method will lock the screen while it shows the splash images. No other screen updates will be possible.
        The image MUST have size exactly equal to 128x128 pixels.
        The image MUST have mode GREYSCALE. RGB will cause exceptions
        """
        # acquire screen lock
        if images is None:
            images = self.splash_logos
        duration = self.splash_duration / len(images)
        for img in images:
            logger.debug("SPLASH -> " + img)
            image_plash_logo = Image.open(img)  # TODO activate this line
            self.OLED.OLED_ShowImage(image_plash_logo, 0, 0)  # TODO activate this line
            time.sleep(duration)
            self.clear_oled()

    def get_font_size(self, font_name, text, max_width):
        font_size = 8
        font = ImageFont.truetype(font_name, font_size)
        while font.getsize(text)[0] < max_width:
            # iterate until the text size is just larger than the criteria
            font_size += 1
            font = ImageFont.truetype(font_name, font_size)
        # step back to be within bounds
        self.font_header_size = font_size - 1
        return ImageFont.truetype(font_name, font_size - 1), self.font_header_size

    def get_host_image(self):
        if self.img_host is None:
            self.img_host = Image.new("L", (128, 128), 0)  # blank black image
            drawing = ImageDraw.Draw(self.img_host)
            drawing.rectangle([(0, 0), (127, 10)], fill=255, outline=255, width=2)
            drawing.rectangle([(0, 10), (127, 40)], fill=None, outline=255, width=2)
            header_start_pos = (128 - self.font_h1.getsize(self._data.host.hostname)[0]) / 2
            drawing.text((header_start_pos, 11), self._data.host.hostname, font=self.font_h1, fill=255)
            drawing.rectangle([(0, 28), (127, 40)], fill=255, outline=255, width=2)
            drawing.text((10, 50), "OS:", font=self.font_std, fill=255)
            drawing.text((20, 66), self._data.host.os, font=self.font_std, fill=255)
            drawing.text((10, 84), "UPTIME:", font=self.font_std, fill=255)
            drawing.text((20, 100), self._data.host.up_time, font=self.font_std, fill=255)
            return self.img_host
        else:
            drawing = ImageDraw.Draw(self.img_host)
            drawing.rectangle([(20, 100), (128, 128)], fill=0, outline=0, width=2)
            drawing.text((20, 100), self._data.host.up_time, font=self.font_std, fill=255)
            return self.img_host

    def get_network_image(self):
        if self.img_network is None:
            self.img_network = Image.new("L", (128, 128), 0)  # blank black image
            drawing = ImageDraw.Draw(self.img_network)
            drawing.rectangle([(0, 0), (127, 10)], fill=255, outline=255, width=2)
            drawing.rectangle([(0, 10), (127, 40)], fill=None, outline=255, width=2)
            header_start_pos = (128 - self.font_h1.getsize(self._data.host.friendly_internet)[0]) / 2
            drawing.text((header_start_pos, 11), self._data.host.friendly_internet, font=self.font_h1, fill=255)
            drawing.rectangle([(0, 28), (127, 40)], fill=255, outline=255, width=2)

        drawing = ImageDraw.Draw(self.img_network)
        drawing.rectangle([(0, 66), (128, 128)], fill=0, outline=0, width=2)
        drawing.text((15, 50), "IP:", font=self.font_std, fill=255)
        drawing.text((5, 66), self._data.host.ip, font=self.font_std, fill=255)
        drawing.text((15, 84), "MAC:", font=self.font_std, fill=255)
        drawing.text((5, 100), self._data.host.mac_address, font=self.font_std, fill=255)
        return self.img_network

    def get_cpu_image(self):
        if self.img_cpu is None:
            self.img_cpu = Image.new("L", (128, 128), 0)  # blank black image
            drawing = ImageDraw.Draw(self.img_cpu)
            icon = Image.open('temp.bmp', 'r')
            icon_h = icon.size[1]
            h_offset = 0
            if icon_h < 128:
                h_offset = (128 - icon_h) / 2
                self.img_cpu.paste(icon, (1, h_offset))
        
        drawing = ImageDraw.Draw(self.img_cpu)
        drawing.rectangle([(36, 42), (128, 73)], fill=0, outline=0, width=2)
        drawing.rectangle([(42, 92), (128, 128)], fill=0, outline=0, width=2)
        drawing.text((36, 42),
                     self._data.cpu.temp + " C", font=self.font_xl, fill=255)
        drawing.text((42, 92), "load = " + str(self._data.cpu.load) + "%", font=self.font_std, fill=255)
        return self.img_cpu

    def get_disk_image(self):
        if self.img_disk is None:
            self.img_disk = Image.new("L", (128, 128), 0)  # blank black image
            drawing = ImageDraw.Draw(self.img_disk)
            icon = Image.open('sdcard.bmp', 'r')
            icon_h = icon.size[1]
            h_offset = 0
            if icon_h < 128:
                h_offset = (128 - 10 - icon_h) / 2
            self.img_disk.paste(icon, (1, h_offset))

        drawing = ImageDraw.Draw(self.img_disk)
        drawing.rectangle([(49, 45), (128, 75)], fill=0, outline=0, width=2)
        drawing.rectangle([(0, 100), (128, 128)], fill=0, outline=0, width=2)
        drawing.text((49, 45), str(self._data.fs.percent) + "%", font=self.font_xl, fill=255)
        drawing.text((2, 100), self._data.fs.friendly_fs_size(), font=self.font_std, fill=255)
        return self.img_disk

    def clear_oled(self):
        """
        Clear screen (black)
        :return: None
        """
        self.OLED.OLED_Clear()
        return None

    def off(self):
        """
        Pauses screen updates
        :return: None
        """
        self._activate_screen = False
        self._display_event.clear()  # Tell internal thread that it should sleep
        logger.debug("screen turned off")
        self.clear_oled()

    def close(self):
        """
        Stops the internal thread, This object is no longer useful and should be disposed.
        :return:
        """
        self._internal_thread_stop()
        logger.debug("OLED thread stopped!")

    def __exit__(self, exc_type, exc_value, traceback):
        self._internal_thread_stop()
        logger.debug("OLED thread stopped!")
