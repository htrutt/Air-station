import serial
from serial.tools.list_ports import grep
from influxdb import InfluxDBClient

VID = "1a86"
PID = "7523"


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

            self._port = serial.Serial(self._port_path)
            self.db_client = db_client  # type: InfluxDBClient
            self._read = True

        except serial.SerialException as e:
            print(e)
            raise

    def read_port(self):
        while self._read:
            rcv = self._port.read(10)
            print("\r\nYou received:")
            print(rcv)

            try:
                PM2_5, PM10 = self._parse_data(rcv)
                self._save_to_db(PM2_5, PM10)
            except InvalidDataException as e:
                print("Invalid data received")

    def _save_to_db(self, PM2_5, PM10):
        json_ojbect =[{
                "measurement": "ParticuleData",
                "fields": {
                    "PM2_5": PM2_5,
                    "PM10": PM10
                }
            }]

        self.db_client.write_points(points=json_ojbect, time_precision="s")

    def _parse_data(self, data):
        if bytes([data[0]]) == b'\xAA' and bytes([data[1]]) == b'\xC0' and bytes([data[9]]) == b'\xAB':
            calculated_check = 0

            for i in range(2, 8, 1):
                calculated_check += data[i]

            if (calculated_check % 256) == data[8]:
                PM2_5 = (data[3] * 256 + data[2]) / 10
                PM10 = (data[5] * 256 + data[4]) / 10
                print("Received valid data PM2,5 {} PM10 {}".format(PM2_5, PM10))
                return PM2_5, PM10

        raise InvalidDataException

    def stop(self):
        self._read = False
