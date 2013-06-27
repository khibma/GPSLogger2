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

def notUsed():

    col = (('Red' , lcd.RED) , ('Yellow', lcd.YELLOW), ('Green' , lcd.GREEN),
           ('Teal', lcd.TEAL), ('Blue'  , lcd.BLUE)  , ('Violet', lcd.VIOLET),
           ('Off' , lcd.OFF) , ('On'    , lcd.ON))

    btn = ((lcd.SELECT, 'Select', lcd.ON),
           (lcd.LEFT  , 'Left'  , lcd.RED),
           (lcd.UP    , 'Up'    , lcd.BLUE),
           (lcd.DOWN  , 'Down'  , lcd.GREEN),
           (lcd.RIGHT , 'Right' , lcd.VIOLET))

    return


def go():
	print "here we go"

	lcd = Adafruit_CharLCDPlate()
	lcd.begin(16, 2)
	lcd.clear()
	lcd.message("Welcome! Press a\nbutton to start")

	#prev = -1
	sleep(1)
	i=0
	lcd.ON
	while True:
		if (lcd.buttonPressed(lcd.SELECT)):
			lcd.clear()
			lcd.message('select...exit')
			sleep(2)
			lcd.backlight(lcd.OFF)
			sleep(2)
			break

		if (lcd.buttonPressed(lcd.RIGHT)):
		    lcd.clear()
		    lcd.ON
		    lcd.message('Your IP address:\n %s' % _IP())

		if (lcd.buttonPressed(lcd.LEFT)):
		    lcd.clear()
		    lcd.ON
		    lcd.message('The time:\n%s' % strftime('%y/%m/%d %I:%M %p', gmtime()))
		    # Once collecting GPS coords correctly, get the time from GPS dict, not the Pi.

		if (lcd.buttonPressed(lcd.UP)):
			while not lcd.buttonPressed(lcd.SELECT):
				lcd.clear()
				lcd.ON
				try:
					msg = push (gpsd, fsURL, userName, passWord, pushOnConnect)
					content = str("{0:.3f},{1:.3f}\n{2}").format(msg[0], msg[1], msg[2])					
					#content = "{},{}\n{}".format(msg[0], msg[1], msg[2])
				except Exception, e:
					print str(e)
					content = "cant get lat/lon"
				lcd.message(content +str(i))
				i+=1
				sleep(10)


		if (lcd.buttonPressed(lcd.DOWN)):
			lcd.clear()
			content = _WEATHER(gpsd.fix.latitude, gpsd.fix.longitude)
			lcd.message(content)

	lcd.backlight(lcd.OFF)



if __name__ == '__main__':
    # When script is run as-is, assume its being started on boot
    # and we want it to be fault tolerant and run forever (or till its a mess then quit)

	faults = 0
	lastFault = 0
	gpsp = GpsPoller()

	# run forever
	while True :
		try:
 			gpsp.start()
 			go()
		except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
			print "\nKilling Thread..."
			gpsp.running = False
			gpsp.join() # wait for the thread to finish what it's doing

		except Exception, e:
			print str(e)
			print "its all over"
			gpsp.running = False
			gpsp.join()
			break # forget this nonsense logic right now ..just break for testing
			if lastFault == 0:
				# enter this only on first fault.
				faults += 1
			else:
				now = datetime.datetime.now()
				diff = now - lastFault

			# If a fault happens with 30 seconds, theres probably a serious issue
			# add to the counter which triggers a break
			# If its been more than 30seconds since the last fault, reset it to 1 fault
			if diff.seconds < 30:
				print "fault"
				faults +=1
			else:
				# reset faults
				faults = 1

			lastFault = datetime.datetime.now()

			if faults >=3:
				# quit the entire program.
				break
			#pass




