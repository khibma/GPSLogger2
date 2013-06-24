from gps import *
session = gps() # assuming gpsd running with default options on port 2947
session.stream(WATCH_ENABLE|WATCH_NEWSTYLE)
report = session.next()
print report

import threading
from time import sleep

class GpsPoller(threading.Thread):
    

    def __init__(self):
        threading.Thread.__init__(self)
        self.session = gps(mode=WATCH_ENABLE)
        self.current_value = None
    
    def get_current_value(self):
        return self.current_value
    
    def run(self):
        try:
            while True:
                self.current_value = session.next()
                sleep(0.3) # tune this, you might not get values that quickly
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            pass

def getGPSPoint():

    gpsp = GpsPoller()
    gpsp.start()
    # gpsp now polls every .2 seconds for new data, storing it in self.current_value
    i = 5
    while i < 10:
       # In the main thread, every 5 seconds print the current value
        time.sleep(5)
        try:
            print gpsp.get_current_value()
            print "lat: {}, long: {}".format(gpsp.get_current_value()['lat'], gpsp.get_current_value()['lon'])
            with open('out.txt', 'w') as gpsFile:
                gpsFile.write(str(gpsp.get_current_value()['lat'])+','+str(gpsp.get_current_value()['lon']))
                i+=1
        except:
            print "looks like gps not ready"
            i+=1
            
if __name__ == '__main__':
    # test, test
    
    while i < 10:   
        print getGPSPoint()
        i+=1
        sleep(3)
            
