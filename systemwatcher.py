#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
import customtypes
import eventclass
import platform
import socket
import psutil
import os
import logging


logger = logging.getLogger(__name__)


class SystemWatcher(object):
    def __init__(self, _update_delay=2, start_monitor=False):
        """
        Reads information from the system at regular intervals.
        Can be started/stopped by using [start_monitoring] and [stop_monitoring].
        By subscribing to the [ValueChanged] Event, you can be notified when a value is updated.
        Note: [ValueChanged] is only triggered once per interval even if more then one value is updated.
        All the gathered data can be read/retrieved from property [this.system_info].
        :param _update_delay (int): Sleep duration in seconds while checking for updates
        :param start_monitor (bool): Sleep duration in seconds while checking for updates
        """
        self._update_delay = _update_delay
        self.system_info = customtypes.SystemInfo()
        self.ValueChanged = eventclass.Event()
        self._delay_lock = threading.Lock()
        self._thread = None
        logger.info("SystemWatcher Init(delay={}, start_monitor={})".format(_update_delay, start_monitor))
        if start_monitor:
            self.start_monitoring()

    @property
    def update_delay(self):
        return self._update_delay

    @update_delay.setter
    def update_delay(self, val):
        with self._delay_lock:
            self._update_delay = val

    def start_monitoring(self):
        """
        Starts monitoring CPU, DISK, HOST and internet connectivity in a separate thread.
        :return: self
        """
        logger.info("polling started...")
        self._thread = threading.Thread(target=self._poll_values)  # , args=("task",))
        self._thread.do_run = True
        self._thread.start()
        return self

    def stop_monitoring(self):
        """
        Stops thread that monitors CPU, DISK, HOST and internet connectivity.

        :return: self
        """
        if self._thread is not None and self._thread.isAlive():  # is_alive() in Python 2.6+
            logger.info("polling stopped")
            self._thread.do_run = False
            self._thread.join()
            self._thread = None
        return self

    @staticmethod
    def prop_delta(field, old_value, new_value, my_list):
        if old_value != new_value:
            my_list.append(customtypes.FieldUpdates(field, old_value, new_value))
            return new_value
        return old_value

    def _update_host_fs(self):
        """
        Reads information about HOST and DISK usage
        :return: None
        """
        values_updated = []
        self.system_info.host.os = self.prop_delta("os", self.system_info.host.os, platform.system(), values_updated)
        self.system_info.host.hostname = self.prop_delta(
            "hostname", self.system_info.host.hostname, platform.node(), values_updated)
        self.system_info.host.ip = self.prop_delta("ip", self.system_info.host.ip, self._get_ip(), values_updated)
        self.system_info.host.mac_address = self.prop_delta(
            "mac_address", self.system_info.host.mac_address, self.get_mac_address(), values_updated)

        t, u, f, p = psutil.disk_usage(".")
        self.system_info.fs.free = self.prop_delta("free", self.system_info.fs.free, f, values_updated)
        self.system_info.fs.used = self.prop_delta("used", self.system_info.fs.used, u, values_updated)
        self.system_info.fs.total = self.prop_delta("total", self.system_info.fs.total, t, values_updated)
        self.system_info.fs.percent = self.prop_delta("percent", self.system_info.fs.percent, p, values_updated)
        return values_updated

    def _update_cpu_internet_uptime(self):
        """
        Reads information about CPU, UP TIME and INTERNET
        :return: None
        """
        values_updated = []
        self.system_info.cpu.temp = self.prop_delta(
            "temp", self.system_info.cpu.temp, self.get_cpu_temp(), values_updated)
        self.system_info.cpu.load = self.prop_delta(
            "load", self.system_info.cpu.load, psutil.cpu_percent(), values_updated)
        self.system_info.host.boot_time = self.prop_delta(
            "boot_time", self.system_info.host.boot_time, psutil.boot_time(), values_updated)
        self.system_info.host.internet = self.prop_delta(
            "internet", self.system_info.host.internet, self.internet_connected(), values_updated)
        return values_updated

    def _poll_values(self):
        """
        At a interval defined by [self._update_delay], this function calls
        :func:`~systemwatcher.SystemWatcher._update_host_fs` and
        :func:`~systemwatcher.SystemWatcher._update_cpu_internet_uptime`.

        :return: None
        """
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            logger.debug("polling  values from system")
            updates = self._update_host_fs() + self._update_cpu_internet_uptime()  # merge two lists
            filter(None, updates)  # remove empty entries
            with self._delay_lock:
                tmp_delay = self._update_delay

            # if values_updated:
            #     kwargs = {"old": self.system_info.host.ip, "new": "a new IP"}
            #     self.ValueChanged(**kwargs)

            if len(updates) > 0:
                logger.debug("values changed, triggering event!")
                self.ValueChanged(updates)
                del updates[:]
            time.sleep(tmp_delay)
        logger.debug("polling thread stopped")

    @staticmethod
    def _get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    @staticmethod
    def get_mac_address(interface='eth0'):
        try:
            raw_address = open('/sys/class/net/%s/address' % interface).read()
        except:
            raw_address = "00:00:00:00:00:00"
        return raw_address[0:17]

    @staticmethod
    def get_cpu_temp():
        try:
            res = os.popen('vcgencmd measure_temp').readline()
        except:
            res = "0.0"
        return res.replace("temp=", "").replace("'C\n", "")

    @staticmethod
    def internet_connected(host="8.8.8.8", port=53):
        """
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(1)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception as ex:
            logger.error('Exception occurred', exc_info=True)
            return False

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_monitoring()
