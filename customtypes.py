#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import datetime

FieldUpdates = collections.namedtuple("FieldUpdates", ["field", "old_value", "new_value"])


class SystemInfo(object):
    def __init__(self):
        self.host = Host()
        self.cpu = Cpu()
        self.fs = FsSystem()


class Host(object):
    def __init__(self, ip=None, os=None, hostname=None, mac_address=None, boot_time=None, internet=None):
        self.ip = ip
        self.os = os
        self.hostname = hostname
        self.mac_address = mac_address
        self._boot_time = boot_time
        self.internet = internet

    @property
    def boot_time(self):
        if isinstance(self._boot_time, float):
            return datetime.datetime.fromtimestamp(self._boot_time)
        elif isinstance(self._boot_time, datetime.datetime):
            return self._boot_time

    @boot_time.setter
    def boot_time(self, value):
        if isinstance(value, float):
            self._boot_time = datetime.datetime.fromtimestamp(value)
        elif isinstance(value, datetime.datetime):
            self._boot_time = value

    @property
    def friendly_internet(self):
        if self.internet:
            return "ONLINE"
        else:
            return "OFFLINE"

    @property
    def up_time(self):
        """
        Calculates up-time based on self.boot_time and returns it in a human friendly format
        :return: string
        """
        return self.friendly_time_delta(self.boot_time)

    @staticmethod
    def friendly_time_delta(start, end=datetime.datetime.now()):
        up_time = end - start
        years, reminder = divmod(up_time.total_seconds(), 31556926)
        days, reminder = divmod(reminder, 86400)
        hours, reminder = divmod(reminder, 3600)
        minutes, seconds = divmod(reminder, 60)
        ret = ""
        if years > 1:
            ret = str(int(years)) + " years, "
        elif years == 1:
            ret = "1 year, "
        if days > 1:
            ret += str(int(days)) + " days, "
        elif days == 1:
            ret += "1 day, "
        if hours > 1:
            ret += str(int(hours)) + " hours"
        elif hours == 1:
            ret += str(int(hours)) + " hour"
        if ret == "" and minutes > 0:
            ret += str(int(minutes)) + " minutes"
        if ret == "" and seconds > 0:
            ret += str(int(seconds)) + " seconds"
        return ret


class Cpu(object):
    def __init__(self, load=None, temp=None):
        self.temp = temp
        self.load = load


class FsSystem(object):
    def __init__(self, _total=None, used=None, free=None, percent=None):
        self.total = _total
        self.used = used
        self.free = free
        self.percent = percent

    def friendly_fs_size(self):
        return self.sizeof_fmt(self.used) + " of " + self.sizeof_fmt(self.total)

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        """
        return friendly byte size string.
        Example: 1024 -> 1KiB
        :param num: the number to transform
        :param suffix: string to append to the output
        :return:
        """
        # for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
