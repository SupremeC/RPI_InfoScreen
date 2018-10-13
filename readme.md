# DisplayApp for RPI3 and Waveshare 1.5 OLED
This is a small application that displays statistics and status iformation to
a Waveshare 1.5" OLED screen connected to Raspberry Pi 3 via SPI.

![img1](https://i.imgur.com/8Mzzr6Z.png) ![img2](https://i.imgur.com/9evTFRR.png)  ![img3](https://i.imgur.com/FHbf6Ug.png)   ![img4](https://i.imgur.com/dxmdZjk.png)

### Prerequisites
 + Raspberry Pi
 + [Waveshare 1.5 inch OLED display](https://www.waveshare.com/1.5inch-OLED-Module.htm) (grayscale)

 
 ### Wiring
 + Wire up OLED display according to the SPI documentation for the Waveshare display.
 + Power LED (red) is wired via a resistor to 5V.
 + System LED (green) is wired to BCM PIN XX.
 + Activity LED (orange) is wired to BCM PIN XX.

### Requires these modules:
 + psutil module
 + Paho MQTT module
 + PILLOW


### Installation part 1
 * Start with a freshly updated system `sudo apt-get update`
 * Enable SPI or I2C bus on the Raspberry depending on how you connect the display
   * `sudo raspi-config`
   * interfacing options -> Enable SPI or I2C
 * Install psutil `pip install psutil`
 * Install Paho MQTT `pip install paho-mqtt`
 * PILLOW `sudo apt-get install python-pil`

### Installation this application
+ TODO - as soon as I get some free time :)


### Wishlist (not implemented)
 + this
 + that
