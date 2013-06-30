from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from time import sleep, gmtime, strftime
import datetime
import threading
import os
import ConfigParser


# Custom modules for project
from getIP import IP2 as _IP
from weather import getWeather as _WEATHER
from pushPoints import push


# initalize the GPS...
from gps import *
gpsd = None #seting the global variable

# load global vars
config = ConfigParser.ConfigParser()
config.read("settings.ini")
fsURL = config.get("AGOL", "fsURL")
userName = config.get("AGOL", "user")
passWord = config.get("AGOL", "pass")
fname = config.get("POINTS", "fname")
pCollectTime = config.get("POINTS", "pCollTime")
pushOnConnect = config.get("POINTS", "pushIfWWW")


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd #bring it in scope
        gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
          gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer


def go():
	print "here we go"

	lcd = Adafruit_CharLCDPlate()
	lcd.begin(16, 2)
	lcd.clear()
	lcd.message("UP=LOG,LFT=TIME\nDOWN=Wtr,RGHT=IP")

	sleep(1)
	i=0
	lcd.ON
	while not (lcd.buttonPressed(lcd.SELECT)):

		if (lcd.buttonPressed(lcd.RIGHT)):
		    lcd.clear()
		    lcd.message('Your IP address:\n %s' % _IP())

		if (lcd.buttonPressed(lcd.LEFT)):
		    lcd.clear()
		    lcd.message('The time:\n%s' % strftime('%y/%m/%d %I:%M %p', gmtime()))
		    # Once collecting GPS coords correctly, get the time from GPS dict, not the Pi.

		if (lcd.buttonPressed(lcd.UP)):
			out = True
			while out:
				lcd.clear()
				try:
					msg = push (gpsd, fsURL, userName, passWord, pushOnConnect)
					content = str("{0:.3f},{1:.3f}\n{2}").format(msg[0], msg[1], msg[2])
				except Exception, e:
					print str(e)
					content = "cant get lat/lon"
				lcd.message(content +str(i))
				### press DOWN 1 second after an updated msg to quit logging
				sleep(1)
				if (lcd.buttonPressed(lcd.DOWN)):
					out = False
					lcd.message("stopped collecting")
				###
				i+=1
				sleep(int(pCollectTime))


		if (lcd.buttonPressed(lcd.DOWN)):
			lcd.clear()
			content = _WEATHER(gpsd.fix.latitude, gpsd.fix.longitude)
			lcd.message(content)


	lcd.clear()
	lcd.message('select called\n.....exit')
	sleep(3)
	lcd.backlight(lcd.OFF)
	return False



if __name__ == '__main__':
    # When script is run as-is, assume its being started on boot

	gpsp = GpsPoller()
	itsOver = True

	# run forever
	while itsOver :
		try:
 			gpsp.start()
 			itsOver = go()

		except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
			print "\nKilling Thread..."
			gpsp.running = False
			gpsp.join() # wait for the thread to finish what it's doing

		except Exception, e:
			print str(e)
			print "its all over"
			gpsp.running = False
			gpsp.join()
			break

	# One last check to shut down the GPS if it didnt get shut down previously
	if gpsp.running == True:
		gpsp.join()



