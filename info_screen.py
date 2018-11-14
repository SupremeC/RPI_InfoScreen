#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# | file       :   info_screen.py
# | version    :   V1.0
# | date       :   2018-10-15
# | function   :   Show statistics on Waveshare 1.5inch OLED
# |					To preserve OLED screen life the display is turned off unless
# |					motion is detected (via MQTT).
# |
# | Learn more at https://github.com/SupremeC/RPI_InfoScreen/
#
# Requires psUtil.   Install: 	sudo apt-get python-psutil
# Requires pahoMQTT. Install:	sudo apt install python-pip
# 								pip install paho-mqtt
#
# INFO:
# Collects various information about the system and displays the info on the screen
#
import time
import os
import signal
import logging.config
import systemwatcher
import oledmanager
import paho.mqtt.client as paho
import RPi.GPIO as GPIO


def script_home_path():
    return os.path.dirname(os.path.realpath(__file__))

def path_join(filename, basedir=script_home_path()):
    return os.path.join(basedir, filename)

# CONSTANTS
LOGGING_CONFIG_FILE = path_join("logging_config.ini")
MQTT_SUBSCRIBE_TOPIC = "home/basement/serverroom/motionsensor"
MQTT_BROKER = ("192.168.1.170", 1883, 60)  # (host, port, timeout)
REFRESH_INTERVAL = 2  # seconds
SYSTEM_RUNNING_LED_PIN = 26  # BCM PIN
SYSTEM_ACTIVITY_LED_PIN = 6  # BCM PIN


# GLOBALS
mqtt_client = None
watcher = None
oled_screen = None


# Logging setup
logging.config.fileConfig(fname=LOGGING_CONFIG_FILE, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


try:
    def main():

        # Turn on front panel LED to signal that system=ON.
        system_running_led(True)

        # Init OLED-screen and show splash image.
        global oled_screen
        oled_screen = oledmanager.OledManager(5, [path_join("icons/rpi_bw_mono.bmp"), path_join("icons/rpilogo.bmp")])

        # monitor interesting key data about the system.
        # Default monitor state is OFF. (set to ON when "motion" is detected)
        global watcher
        watcher = systemwatcher.SystemWatcher(30, False)
        watcher.ValueChanged += update_screen  # call this function when value(s) changed

        # Listens for motion detection is server room.
        # On "motion" detected the screen will display.
        mqtt_setup()

        # Keep alive until we receive a signal.
        # The signal most likely to be received is SIGTERM, but as for now
        # we don't really care which one it is.
        # Cleanup will happen in the "FINALLY" block.
        signal.pause()


    def mqtt_setup():
        global mqtt_client
        mqtt_client = paho.Client(client_id="RPI-A_OLEDScreen", clean_session=False, userdata=None)
        mqtt_client.enable_logger(logger)
        mqtt_client.on_connect = mqtt_on_connect
        mqtt_client.on_subscribe = mqtt_on_subscribe
        mqtt_client.on_message = mqtt_on_message
        mqtt_client.connect(MQTT_BROKER[0], MQTT_BROKER[1], MQTT_BROKER[2])
        mqtt_client.loop_start()
        mqtt_client.on_disconnect = mqtt_on_disconnect

    def mqtt_on_connect(client, userdata, flags, rc):
        logger.info("MQTT CONNACK received with code %d." % rc)
        client.subscribe(MQTT_SUBSCRIBE_TOPIC, qos=1)

    def mqtt_on_disconnect(client, userdata, rc):
        if rc != 0:  # unexpected disconnect
            logger.warning("unexpected disconnect from MQTT server " + " ".join(MQTT_BROKER))
            logger.info("Trying to reconnect to MQTT server...")
            client.reconnect()
            time.sleep(30)

    def mqtt_on_subscribe(client, userdata, mid, granted_qos):
        logger.info("MQTT Subscribed: " + str(mid) + " " + str(granted_qos))


    def mqtt_on_message(client, userdata, msg):
        global oled_screen
        logger.info(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        if msg.topic == MQTT_SUBSCRIBE_TOPIC and msg.payload == "motion":
            watcher.start_monitoring()
        else:
            watcher.stop_monitoring()
            oled_screen.off()

    def update_screen(args, **kwargs):  # TODO remove this
        global oled_screen
        global watcher
        oled_screen.update(watcher.system_info)

    def system_running_led(state_on):
        logger.debug("SYSTEM RUNNING LED " + str(state_on))
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        if state_on:
            GPIO.setup(SYSTEM_RUNNING_LED_PIN, GPIO.OUT)  # green LED
            GPIO.output(SYSTEM_RUNNING_LED_PIN, GPIO.HIGH)
        else:
            GPIO.setup(SYSTEM_RUNNING_LED_PIN, GPIO.OUT)  # green LED
            GPIO.output(SYSTEM_RUNNING_LED_PIN, GPIO.LOW)

    if __name__ == "__main__":
        main()

except KeyboardInterrupt:
    logger.info("Keyboard Interrupt. exiting program")
except:
    logger.error('Exception occurred', exc_info=True)
    raise
finally:
    # stop watcher
    logger.info("starting cleanup...")
    watcher.stop_monitoring()
    del watcher

    # dispose MQTT client
    mqtt_client.unsubscribe(MQTT_SUBSCRIBE_TOPIC)
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
    del mqtt_client

    # turn off OLED screen and kill background thread.
    system_running_led(False)
    global oled_screen
    oled_screen.close()
    oled_screen.clear_oled()
    GPIO.cleanup()  # this ensures a clean exit
    logger.info("Done cleaning. Exiting")
