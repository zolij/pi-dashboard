import os
import sqlite3
import time

from openweather import OpenWeather

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class TempLogger:
    _device_file = '/sys/bus/w1/devices/28-041663737dff/w1_slave'
    _db_name = __location__ = '{0}/templog.db'.format(__location__)

    def __init__(self):
        pass

    def get_temp(self):
        try:
            file_obj = open(self._device_file, 'r')
            lines = file_obj.readlines()
            file_obj.close()
        except:
            return None

        # get the status from the end of line 1
        status = lines[0][-4:-1]

        # is the status is ok, get the temperature from line 2
        if status == "YES":
            temp_str = lines[1][-6:-1]
            return float(temp_str) / 1000
        else:
            return None

    def save_data_to_database(self):
        ow = OpenWeather()

        internal = self.get_temp()
        external = ow.current()
        conn = sqlite3.connect(self._db_name)
        curs = conn.cursor()
        curs.execute("INSERT INTO temps values(datetime('now'), (?), (?))", (internal, external))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    logger = TempLogger()
    logger.save_data_to_database()
