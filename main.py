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

def getFileName():
	# finds the last file created
	i = 0

	for i in range(100,0,-1):
		try:
			tryFile = "points_{}.csv".format(i)
			with open(tryFile, 'r') as f:
				return tryFile
		except IOError: pass

	return "points_0.csv"


def go(filename):
	print "here we go"


	lcd = Adafruit_CharLCDPlate()
	lcd.begin(16, 2)
	lcd.clear()
	lcd.message("UP=LOG,LFT=fixWW\nDWN=File,RGT=Info")

	sleep(1)
	i=0
	lcd.ON
	prev = -1

	while not (lcd.buttonPressed(lcd.SELECT)):
		# The ELSE on all button pushes which handle multiple clicks is the first entry point

		if (lcd.buttonPressed(lcd.RIGHT)):
			# cycle through: WEATHER, IP, and TIME then repeat
			lcd.clear()

			if prev == "r1":
				prev = "r2"
				lcd.message('Your IP address:\n %s' % _IP())
				sleep(1)
			elif prev == "r2":
				prev = -1
				#lcd.message('The time:\n%s' % strftime('%y/%m/%d %I:%M %p', gmtime()))
				lcd.message('The time:\n%s' % str(gpsd.utc))
				sleep(1)
			else:
				prev = "r1"
				content = _WEATHER(gpsd.fix.latitude, gpsd.fix.longitude)
				lcd.message(content)
				sleep(1)


		if (lcd.buttonPressed(lcd.LEFT)):
			# reconnects the internet if disconnected
			lcd.clear()

			if prev == 'l1':
				prev = -1
				lcd.message("reconneting internet")
				# to be tested, what happens if cell phone internet drops, will it reconnect

			else:
				prev = 'l1'
				sats = gpsd.satellites
				gSatCount = 0
				for item in sats:
				    if item.used == True:
				        gSatCount += 1
				totSats = len(sats)
				lcd.message("%s Sats \n overhead" % totSats)



		if (lcd.buttonPressed(lcd.UP)):
			# starts the GPS logging
			prev = 'u1'
			while prev == 'u1':
				lcd.clear()
				try:
					msg = push (gpsd, fsURL, userName, passWord, filename)
					content = str("{0:.3f},{1:.3f}\n{2}").format(msg[0], msg[1], msg[2])
				except Exception, e:
					print str(e)
					content = "cant get lat/lon"
				lcd.message(content +str(i))
				### press DOWN 1 second after an updated msg to quit logging
				sleep(1)
				if (lcd.buttonPressed(lcd.UP)):
					prev = -1
					lcd.clear()
					lcd.message("stopped\ncollecting")
				###
				i+=1
				sleep(int(pCollectTime))

			'''
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
					lcd.clear()
					lcd.message("stopped\ncollecting")
				###
				i+=1
				sleep(int(pCollectTime))
			'''

		if (lcd.buttonPressed(lcd.DOWN)):
			# shows how many lines in current .CSV file
			# 2nd push starts a new file
			print prev
			lcd.clear()
			if prev == "d1":
				prev = -1
				curNum = os.path.splitext(filename[filename.rfind('_')+1:])[0]
				newNum = int(curNum) +1
				filename= filename.replace(str(curNum), str(newNum))
				lcd.message("now using:\n %s" % filename)
				sleep(1)

			else:
				prev = 'd1'
				try:
					with open(filename) as f:
						for i, l in enumerate(f):
							pass
					lines = i+1
				except IOError: lines = "???"

				lcd.message("f: %s has\n %s lines" % (filename, lines))
				sleep(1)



	lcd.clear()
	lcd.message('select called\n.....exit')
	sleep(3)
	lcd.backlight(lcd.OFF)
	lcd.message('')
	return False



if __name__ == '__main__':
    # When script is run as-is, assume its being started on boot

	filename = getFileName()

	gpsp = GpsPoller()
	itsOver = True

	# run forever
	while itsOver :
		try:
 			gpsp.start()
 			itsOver = go(filename)
 			gpsp.running = False
			gpsp.join() # wait for the thread to finish what it's doing
			print itsOvercd

		except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
			print "\nKilling Thread..."
			gpsp.running = False
			gpsp.join() # wait for the thread to finish what it's doing
			print "ctrl-c exit"

		except Exception, e:
			print str(e)
			gpsp.running = False
			gpsp.join()
  			print "out in a bad way"
			break


	# One last check to shut down the GPS if it didnt get shut down previously
	if gpsp.running == True:
		gpsp.join()
	print "program done!"



