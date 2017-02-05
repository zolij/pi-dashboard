import urllib2
import json

from openweatherconfig import config


def _fetch_json(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return response.read()


class OpenWeather:
    _weather = None

    def __init__(self):
        weather_data = _fetch_json("http://api.openweathermap.org/data/2.5/weather?q=" + config[
            'location'] + "&units=metric&APPID=" + config['api'])
        self._weather = json.loads(weather_data)
        pass

    def current(self):
        return self._weather['main']['temp']
