# Utility function to get the weather
# Pick your poision......
#   getYahooWeather : Yahoo Weather requires knowledge of city code. This can be implemented via lookup
#   getForecastIOWeather : ForecastIO limits to 1000 free requests per day
#   getWunderlandWeather : WunderlandWeather limits to 500 free requests per day
#   getWeather : helper function to try both ForeCastIO and WunderLand

import urllib, json
import ConfigParser

# get api keys from settings.ini
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("settings.ini")
forecastKey = config.get("WEATHER", "forecastIOapiKey")
wundergroundKey = config.get("WEATHER", "wundergroundapiKey")

def getYahooWeather():
	# Hard coded to get weather in Redlands, CA
	# Would have to implement a look up o the ID/location

	locationID = 12796451
	URL = 'http://weather.yahooapis.com/forecastjson?w=12796451'
	URL2 ='http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20location="USCA0923"&format=json'

	try:
		response = urllib.urlopen(URL2)
		jResponse = json.loads(response.read())

		return jResponse['query']['results']['channel']['item']['condition']['temp']
	except:
		return "No weather found"

def getForecastIOWeather(lat=34.0555693, lon=-117.1825381, apiKey=forecastKey):
	# Uses Redlands, CA if nothing passed in

	URL = "https://api.forecast.io/forecast/{}/{},{}".format(apiKey, lat, lon)

	try:
		response = urllib.urlopen(URL)
		jResponse = json.loads(response.read())

		return "{}F\n(unknown local)".format(jResponse["currently"]["temperature"])
	except:
		return 0

def getWundergroundWeather(lat=34.0555693, lon=-117.1825381, apiKey=wundergroundKey):
	# Use Redlands CA if nothing passed in
	# Note, this will only work in US. Review city lookup outside the US

	URL = "http://api.wunderground.com/api/{}/geolookup/q/{},{}.json".format(apiKey, lat, lon)
	try:
		response = urllib.urlopen(URL)
		jResponse = json.loads(response.read())
		state = jResponse["location"]["state"]
	 	city = jResponse["location"]["city"]

 		cityURL = "http://api.wunderground.com/api/{}/conditions/q/{}/{}.json".format(apiKey, state, city)
		cityResponse = urllib.urlopen(cityURL)
		jCityResponse = json.loads(cityResponse.read())
		currentTemp = jCityResponse['current_observation']['temperature_string']

		return "{} in\n  {}".format(currentTemp, city)
	except:
		return 0


def getWeather(lat, lon):
	# Use this generic function to try weather from both sources

	weather = getWunderlandWeather(lat, lon)
	if weather == 0:
		weather = getForecaseIOWeather(lat, lon)
		if weather == 0:
			weather = "No weather report\navailable "

	return weather



if __name__ == '__main__':
	# test, test

	temp = getYahooWeather()
	print 'the temp: {}F'.format(temp)

	temp2 = getForecastIOWeather(34.0555693, -117.1825381, forecastKey)
	print temp2

	temp3 = getWundergroundWeather(34.0555693, -117.1825381, wundergroundKey)
	print temp3

	temp4 = getWeather(34.0555693, -117.1825381)
	print temp4
