import csv
import datetime

import serial
from serial.tools.list_ports import grep

VID = "1a86"
PID = "7523"


class InvalidDataException(Exception):
    def __init__(self):
        super(InvalidDataException, self).__init__("Invalid data received")


class ParticuleSensor:

    def __init__(self):
        try:
            ports = list(serial.tools.list_ports.comports())

            for p in ports:
                if VID and PID in p.hwid:
                    self._port_path = p.device

            self._port = serial.Serial(self._port_path)
            self._current_day = None

        except serial.SerialException as e:
            print(e)
            raise

    # TODO break out the writing to file to be able to save in same file temp + PM data
    def read_port(self):
        while True:
            rcv = self._port.read(10)
            print("\r\nYou received:")
            print(rcv)

            try:
                PM25, PM10 = self._parse_data(rcv)
                self._save_to_file(PM25, PM10)
            except InvalidDataException as e:
                print("Invalid data received")

    def _save_to_file(self, PM25, PM10):
        now = datetime.datetime.now()
        if now.day != self._current_day:
            self._current_day = now.day
            self._file_name = "/tmp/data_{}_{}_{}".format(now.year, now.month, now.day)

        with open(self._file_name, mode='a')as data_file:
            data_file_writer = csv.writer(data_file, delimiter=',')
            data_file_writer.writerow([datetime.datetime.now(), PM25, PM10])

    def _parse_data(self, data):
        if bytes([data[0]]) == b'\xAA' and bytes([data[1]]) == b'\xC0' and bytes([data[9]]) == b'\xAB':
            calculated_check = 0

            for i in range(2, 8, 1):
                calculated_check += data[i]

            if (calculated_check % 256) == data[8]:
                PM25 = (data[3] * 256 + data[2]) / 10
                PM10 = (data[5] * 256 + data[4]) / 10
                print("Received valid data PM2,5 {} PM10 {}".format(PM25, PM10))
                return PM25, PM10

        raise InvalidDataException
