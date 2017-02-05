import json
import os
import psutil
import time
import urllib2
import sqlite3

from flask import Flask, render_template
from openweatherconfig import config

app = Flask(__name__)


def fetch_json(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return response.read()


class System:
    def __init__(self):
        pass

    def free_memory(self):
        mem = psutil.virtual_memory()
        return mem.available

    def load(self):
        return os.getloadavg()

    def temp(self):
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.readline().split()[0])

        return temp

    def uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(time.strftime('%H:%M:%S', time.gmtime(uptime_seconds)))

        return uptime_string


class Temperature:
    _device = '/sys/bus/w1/devices/28-041663737dff/w1_slave'
    _dbname = '/home/zolij/apps/rpi_temp_logger/templog.db'

    def __init__(self):
        pass

    def _get_data(self):
        interval = 24

        conn = sqlite3.connect(self._dbname)
        curs = conn.cursor()
        curs.execute("SELECT * FROM temps WHERE timestamp>datetime('now','-%s hours')" % interval)
        rows = curs.fetchall()
        conn.close()
        return rows

    def _create_table(self, rows):
        chart_table = ""

        for row in rows[:-1]:
            rowstr = "['{0}', {1}],\n".format(str(row[0]), str(row[1]))
            chart_table += rowstr

        row = rows[-1]
        rowstr = "['{0}', {1}]\n".format(str(row[0]), str(row[1]))
        chart_table += rowstr

        return chart_table

    def current_external(self):
        sWeather = fetch_json("http://api.openweathermap.org/data/2.5/weather?q=" + config[
            'location'] + "&units=metric&APPID=" + config['api'])
        jWeather = json.loads(sWeather)
        temp = jWeather['main']['temp']
        return temp

    def current_internal(self):
        try:
            fileobj = open(self._device, 'r')
            lines = fileobj.readlines()
            fileobj.close()
        except:
            return None

        # get the status from the end of line 1
        status = lines[0][-4:-1]

        # is the status is ok, get the temperature from line 2
        if status == "YES":
            tempstr = lines[1][-6:-1]
            tempvalue = float(tempstr) / 1000
            return tempvalue
        else:
            print "Hiba"
            return None

    def graph_data(self):
        records = self._get_data()
        table = self._create_table(records)
        return table


@app.route('/')
def index():
    system = System()
    temperature = Temperature()
    system_vars = {
        'free_memory': system.free_memory(),
        'load': system.load(),
        'temp': system.temp(),
        'uptime': system.uptime()
    }
    temperature_vars = {
        'external': temperature.current_external(),
        'internal': temperature.current_internal(),
        'graph_data': temperature.graph_data()
    }
    return render_template("index.html", system_vars=system_vars, temperature_vars=temperature_vars)


if __name__ == '__main__':
    app.run()
