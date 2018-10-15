# DisplayApp for RPI3 and Waveshare 1.5 OLED
This is a small application that displays statistics and status iformation to
a Waveshare 1.5" OLED screen connected to Raspberry Pi 3 via SPI.
Developed with Python 2 but it should run on Python3 as well.
![img1](https://i.imgur.com/8Mzzr6Z.png) ![img2](https://i.imgur.com/9evTFRR.png)  ![img3](https://i.imgur.com/FHbf6Ug.png)   ![img4](https://i.imgur.com/dxmdZjk.png)

### Prerequisites
 + Raspberry Pi
 + [Waveshare 1.5 inch OLED display](https://www.waveshare.com/1.5inch-OLED-Module.htm) (grayscale)
 + SPI or I2C enabled
     + `sudo raspi-config` -> interfacing options ->  [enable SPI or I2C]

 
 ### Wiring
 + Wire up OLED display according to the SPI or I2C documentation for the Waveshare display.
 + Power LED (red) is wired via a resistor to 5V.
 + System LED (green) is wired to BCM PIN 26.
 + Activity LED (orange) is wired to BCM PIN 6.

### Requires these modules:
 + psutil
 + Paho MQTT
 + PILLOW



### Installation this application
 ```bash 
pip install psutil
pip install paho-mqtt
sudo apt-get install libjpeg-dev  # needed by pillow
pip install pillow
pip install spidev
sudo apt-get install python-smbus i2c-tools

cd /home/pi
mkdir -p projects/displayApp
cd /home/pi/projects
wget https://github.com/SupremeC/RPI_InfoScreen/archive/master.zip
unzip master.zip
mv RPI_InfoScreen-master/* ./displayApp
rm -rf RPI_InfoScreen-master
rm master.zip
 ``` 

### How to use
+ To manually start: `python info_screen.py`
+ To clear the screen (for any reason): `python turn_off_screen.py`
+ To manually trigger 'motion' event:  `mosquitto_pub -t home/basement/serverroom/motionsensor -m motion`

 
### Scheduling
TODO

