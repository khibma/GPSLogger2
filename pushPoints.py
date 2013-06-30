import urllib, urllib2, json, sys, os


def gentoken(tokenUrl, username, password, expiration=60):
    # Classic token generation for consumption later.
    #

    referer = "http://www.mywww.com/"

    query_dict = {'username': username,
                  'password': password,
                  'expiration': str(expiration),
                  'client': 'referer',
                  'referer': referer,
                  #'client': 'requestip',
                  'f': 'json'}

    token = ""
    tokenResponse = urllib.urlopen(tokenUrl, urllib.urlencode(query_dict))
    tokenJson = json.loads(tokenResponse.read())

    if 'error' in tokenJson:
        print "couldnt get token:"
        print tokenJson

    if 'token' in tokenJson:
        token = tokenJson['token']

    return token


def makePayload(gpsdIn):
    # So this obviously has some flaws...
    # 1.. its pretty static
    # 2.. theres a more pythonic way to do tis
    # 3.. see 1, need to check the input dict coming in to match it. But at the same time needs to match the FS online
    # 4.. wouldnt it be nice if it could inspect the FS and make an appropraite payload? 99% sure ill never implement that
    #

    # total satellites in the schema yet....
	# count how many satellites there are and  used
    sats = gpsdIn.satellites

    gSatCount = 0
    for item in sats:
        if item.used == True:
            gSatCount += 1
    totSats = len(sats)

    # average error not in the schema yet....
	# get a real *rough* error apprxomation from x/y
    errAvg = (gpsdIn.fix.epx + gpsdIn.fix.epy) / 2


	# schema must match, could possibly make it more flexible by adding to the settings.ini
    payload = {
      "attributes" : {
        "Name" : 'footag',
        "Lat" : gpsdIn.fix.latitude,
        "Lon" : gpsdIn.fix.longitude,
        "Date" : str(gpsdIn.utc),
        "Speed" : gpsdIn.fix.speed,
        "Elevation" : gpsdIn.fix.altitude,
        "Heading" : gpsdIn.fix.track,
        "NumSatFix" : gSatCount,
        "TotSats" : totSats,
        "errAvg" : errAvg
      },
      "geometry" : {
        "x" : gpsdIn.fix.longitude,
        "y" : gpsdIn.fix.latitude
      }}


    return payload


def writeGPStoFile(inputPayload):
	# If we cant push the point into AGOL for some reason (like theres no internet connection available),
	#  then save the point in a csv file so we can push it up later

	import csv
	att_dict = inputPayload['attributes']

	try:
	   with open('POINTS.csv', 'a'):
  		w = csv.DictWriter(f, att_dict.keys())
		w.writerow(att_dict)

	except IOError:
		with open('POINTS.csv', 'w') as f:
		    w = csv.DictWriter(f, att_dict.keys())
		    w.writeheader()
		    w.writerow(att_dict)
	'''
	with open("mycsvfile.csv", "a") as f:
		w = csv.DictWriter(f, att_dict.keys())
		w.writerow(att_dict)
	'''
	return


def push(gpsdIn, fsURL, username, password, token=None):
    # Add points to the online feature service
    #

    tokenUrl = "https://www.arcgis.com/sharing/rest/generateToken"

    if len(username) > 0 and len(password) > 0:
        token = gentoken(tokenUrl, username, password)

    push = makePayload(gpsdIn)

    submitData = {}
    submitData["Features"] = push
    submitData["f"] = "json"
    submitData["token"] = token

    # submit the request
    submitResponse = urllib2.urlopen(fsURL, urllib.urlencode(submitData))
    jAdd = json.loads(submitResponse.read())

    # this is a little overkill right now as it will parse over multiple inputs
    # however, right now submission is only 1 at a time
    if "addResults" in jAdd:
        if len(jAdd['addResults']) > 0:
            for addItem in jAdd['addResults']:
                if addItem['success'] == True:
					print "Inserted a new objectID {}".format(addItem['objectId'])
					#TEST
					writeGPStoFile(push)

					return [gpsdIn.fix.latitude, gpsdIn.fix.longitude, "uploaded"]

                if addItem['success'] == False:
                    print "Failed to insert:"
                    print addItem['error']['description']

					# write the point to the csv file
                    writeGPStoFile(push)

                    return [gpsdIn.fix.latitude, gpsdIn.fix.longitude, "failed"]

    else:
        # write the point to the csv file
        writeGPStoFile(push)
        print "Couldnt add anything.."
        print jAdd


    return [gpsdIn.fix.latitude, gpsdIn.fix.longitude, "unknown"]


if __name__ == "__main__":
    # test me! (yeah, a lot of repeat code from MAIN.py)

	import threading
 	from gps import *
	import ConfigParser
	gpsd = None

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

	# load global vars
	config = ConfigParser.ConfigParser()
	config.read("settings.ini")
	fsURL = config.get("AGOL", "fsURL")
	userName = config.get("AGOL", "user")
	passWord = config.get("AGOL", "pass")

	gpsp = GpsPoller()
	gpsp.start()

	# push also calls makePayload with the output of of gpsd, so we get back a success or failure on agol point upload
	print push(gpsd, fsURL, userName, passWord, token=None)

	gpsp.running = False
	gpsp.join()

	# the gpsd output looked like this in an old version
	values2Push= {'epx': 11.643, 'epy': 13.885, 'epv': 21.62, 'ept': 0.005,
	              'lon': -117.196381667, 'eps': 27.77, 'lat': 34.057223333,
	              'tag': 'RMC', 'track': 51.74, 'mode': 3, 'time': '2013-06-20T19:16:22.000Z',
	              'device': '/dev/ttyAMA0', 'climb': 0.2, 'alt': 388.9, 'speed': 0.273, 'class': 'TPV'}
