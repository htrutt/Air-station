import time

import requests
import serial
from serial.tools.list_ports import grep
from influxdb import InfluxDBClient

from sds011 import SDS011

VID = "1a86"
PID = "7523"
POST_URL = "https://api.luftdaten.info/v1/push-sensor-data/"

class InvalidDataException(Exception):
    def __init__(self):
        super(InvalidDataException, self).__init__("Invalid data received")


class ParticuleSensor:

    def __init__(self, db_client):
        try:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                raise Exception("No serial port connection found, are you sure the particule sensor is connected?")

            for p in ports:
                if VID and PID in p.hwid:
                    self._port_path = p.device

            self._sensor = SDS011(self._port_path, timeout=2, unit_of_measure=SDS011.UnitsOfMeasure.MassConcentrationEuropean)
            print("SDS011 sensor info:")
            print("Device ID: ", self._sensor.device_id)

            self.db_client = db_client  # type: InfluxDBClient
            self._read = True

        except serial.SerialException as e:
            print(e)
            raise

    def read_port(self):
        while self._read:
            print("Waking up the sensor")
            self._sensor.workstate = SDS011.WorkStates.Measuring
            # Just to demonstrate. Should be 60 seconds to get qualified values.
            # The sensor needs to warm up!
            time.sleep(10)
            while self._read:
                last1 = time.time()
                values = self._sensor.get_values()
                if values is not None:
                    print("Values measured in µg/m³:    PM2.5 {} , PM10 {}".format(values[1], values[0]))
                    self.postData(url=POST_URL, pin=1, PM25=values[1], PM10=values[0])
                    break
                print("Waited %d seconds, no values read, wait 2 seconds, and try to read again" % (
                        time.time() - last1))
                time.sleep(2)
            print("Read was succesfull. Going to sleep for 10 seconds")
            self._sensor.workstate = SDS011.WorkStates.Sleeping
            time.sleep(10)

        print("\nSensor reset to normal")
        self._sensor.reset()
        self._sensor = None


    def postData(self, url, pin, PM25,PM10):
        r = requests.post(url,
                      json={
                          "software_version": "python-dusty 0.0.1",
                          "sensordatavalues": [{"value_type": "P2", "value": PM25},
                                               {"value_type": "P1", "value": PM10}]
                      },
                      headers={
                          "X-Pin": str(pin),
                          "X-Sensor": "raspi-"+self._sensor.device_id,
                      }
                      )
        print("Response code {}".format(r.status_code))
        print("Response  {}".format(r.text))

    def _save_to_db(self, PM2_5, PM10):
        json_ojbect =[{
                "measurement": "ParticuleData",
                "fields": {
                    "PM2_5": PM2_5,
                    "PM10": PM10
                }
            }]

        if self.db_client is not None:
            self.db_client.write_points(points=json_ojbect, time_precision="s")

    def stop(self):
        self._read = False
