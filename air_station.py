#!/bin/python3
from particule_sensor import ParticuleSensor


class AirStation:
    def __init__(self):
        self._particule_sensor = ParticuleSensor()

    def  start_station(self):
        self._particule_sensor.read_port()


if __name__ == '__main__':
    print("Started air station")
    station = AirStation()
    station.start_station()
