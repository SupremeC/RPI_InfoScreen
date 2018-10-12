# DisplayApp for RPI3 and Waveshare 1.5 OLED
This is a small application that displays statistics and status iformation to
a Waveshare 1.5" OLED screen connected to Raspberry Pi 3 via SPI.

### Prerequisites
 + Raspberry Pi
 + Waveshare 1.5 inch OLED display (grayscale)

 
 ### Wiring
 + Wire up OLED display according to the SPI documentation for the Waveshare display.
 + Power lED (red) is wired via a resistor to 5V.
 + System LED (green) is wired to BCM PIN XX.
 + Activity LED (orange) is wired to BCM PIN XX.

### Requires these modules:
 + psutil module
 + Paho MQTT module
 + PILLOW


### Installation part 1
 + Enable SPI or I2C bus on the Raspberry depending on how you connect the display
 ++ sudo raspi-config
 ++ interfacing options -> Enable SPI or I2C
 + Install psutil
 + Install Paho MQTT
 + PILLOW

### Installation this application
+ TODO - as soon as I get some free time :)


### Wishlist (not implemented)
 + this
 + that
