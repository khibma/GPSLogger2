GPSLogger
=========

Raspberry PI GPS Logger with LCD/button control

This project was put together with a Raspberry Pi B, [Adafruit GPS](https://www.adafruit.com/products/746) and [Adafruit LCD 16x2 shield](https://www.adafruit.com/products/772). This was a project put together back in 2013 for a road trip across the US and into Canada. The code in the repo and the hardware haven't been used together since then. This readme is being updated today just as an explanation of the project. One day I may go back and test and cleanup the code.

<a href="https://angp.maps.arcgis.com/apps/Embed/index.html?webmap=3b0e135a85db480aa1334acfa55b010e&amp;extent=-123.7335,22.3283,-58.8263,52.011&amp;zoom=true&amp;scale=false&amp;legend=true&amp;disable_scroll=false&amp;theme=light" style="color:#0000FF;text-align:left" target="_blank">View the map with the logged data points</a>

<img src=https://cloud.githubusercontent.com/assets/2514926/12704676/c5bfa7e6-c82d-11e5-935b-2bf9b17eac88.JPG width=400>
The following information has been ported from my old website into the readme

###Setup the raspberry pi
```
sudo apt-get install python-smbus
sudo apt-get install i2c-tools
sudo apt-get install python-dev
sudo apt-get install python-rpi.gpio
sudo apt-get install gpsd gpsd-clients python-gps
sudo apt-get install git
```
>sudo nano /etc/modules
```
i2c-bcm2708 
i2c-dev
```

###Testing components
You can test the LCD at shell with the following commands:
>sudo modprobe i2c-dev
>sudo i2cdetect -y 1 

See the Adafruit LCD tutorial for more information on setting up the LCDWith the GPS reciever complete, test to make sure it works. 

Note that first attempt it could require a minute or longer to obtain a lock. Make sure it has a good LOS. My GPS is connected via UART, not the USB, so the following change has been made on my Pi.

>sudo nano /boot/cmdline.txt dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait

to:

>dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait

Reboot the Pi again...
>sudo reboot -n

Test that the GPS works...(enable the GPS, and launch cgps. Use Ctrl-C to break out) 
>sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock

>cgps -s

All stuffed into a "charmin" box to sit on the car dash

<img src=https://cloud.githubusercontent.com/assets/2514926/12704675/c42dd88a-c82d-11e5-8177-5f1c1b261f20.jpg width=400>

###Code explained

* **main.py**: this is the entry point to the program. This listens for button clicks and starts functions

* **settings.ini**: various settings and keys are placed here. Developer keys for weather apis, usernames/passwords for AGOL as well as feature service URLs

* **weather.py**: code for 3 different weather services (yahoo, wunderground, and forecastio). Currently wunderground is the go-to weather source with forecast as the backup. You'll have to get your own API key

* **getIP.py**: various different ways to obtain an IP address. The current method used seems to be fitting for the Pi.

* **pushPoints.py**: All the work of collecting points for the gpsd is done here. A dictionary is parsed and pushed both to ArcGIS Online as well as saved to a local CSV file

* **adafruit__.py** : files from adafruit to drive the LCD and buttonsMenu explained quickly....

  * *left*: 1) displays how many sats have a fix. 2) not implemented, will re-connect the internet by firing a script

  * *down* 1) displays the current CSV file and how many lines have been written (1 line = 1 point), 2) increments the file numbering, thus saving to a new CSV file. Good to use if the file gets very large

  * *right* 1) displays the weather, 2) displays your IP address, 3) displays the time (from the GPS...not localized)

  * *up* 1) starts collecting points, 2) will stop collecting points

  * *select* 1) exit the program

* **NOTE:** Since the button listening is poor, sleeps ensure buttons are read. 1 second sleep happens after every button push, so you cannot use buttons rapidly. Also note the only way to break out of point collection is to time the 2nd up press about 1 second after the screen tells of a new point captured.

