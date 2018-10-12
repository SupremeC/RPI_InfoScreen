#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging.config
import systemwatcher
import oledmanager
import paho.mqtt.client as paho
import RPi.GPIO as GPIO
from pympler.tracker import SummaryTracker
tracker = SummaryTracker()

# CONSTANTS
LOGGING_CONFIG_FILE = "logging_config.ini"
MQTT_SUBSCRIBE_TOPIC = "home/basement/serverroom/motionsensor"
MQTT_BROKER = ("192.168.1.170", 1883, 60)  # (host, port, timeout)
REFRESH_INTERVAL = 2  # seconds
SYSTEM_RUNNING_LED_PIN = "fake"


# GLOBALS
mqtt_client = None
watcher = None
oled_screen = None
main_loop_run = True  # Set to False to terminate program


# Logging setup
logging.config.fileConfig(fname=LOGGING_CONFIG_FILE, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


try:
    def main():

        # Turn on front panel LED to signal that system=ON.
        system_running_led(True)

        # Init OLED-screen and show splash image.
        global oled_screen
        oled_screen = oledmanager.OledManager(5, ["rpi_bw_mono.bmp", "rpilogo.bmp"])

        # monitor interesting key data about the system.
        # Default monitor state is OFF. (set to ON when "motion" is detected)
        global watcher
        watcher = systemwatcher.SystemWatcher(30, False)
        watcher.ValueChanged += update_screen  # call this function when value(s) changed

        # Listens for motion detection is server room.
        # On "motion" detected the screen will display.
        mqtt_setup()

        # Loop until someone says stop!
        global main_loop_run
        while main_loop_run:
            time.sleep(30)


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
            GPIO.setup(6, GPIO.OUT)
            GPIO.output(6, GPIO.HIGH)
            GPIO.setup(26, GPIO.OUT)
            GPIO.output(26, GPIO.HIGH)
        else:
            GPIO.setup(6, GPIO.OUT)
            GPIO.output(6, GPIO.LOW)
            GPIO.setup(26, GPIO.OUT)
            GPIO.output(26, GPIO.HIGH)

    if __name__ == "__main__":
        main()

except KeyboardInterrupt:
    logger.info("Keyboard Interrupt. exiting program")
except:
    logger.error('Exception occurred', exc_info=True)
    raise
finally:
    # stop watcher
    logger.info("finally the end")
    watcher.stop_monitoring()
    del watcher

    # dispose MQTT client
    mqtt_client.unsubscribe(MQTT_SUBSCRIBE_TOPIC)
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
    del mqtt_client

    # turn off OLED screen and kill background thread.
    global oled_screen
    oled_screen.close()
    oled_screen.clear_oled()
    del oled_screen
    GPIO.cleanup()  # TODO enable this ensures a clean exit
    time.sleep(2)  # for debugging purposes. (allows console output to complete from child threads. Can be removed.
    tracker.print_diff()