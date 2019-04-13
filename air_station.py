#!/bin/python3
from particule_sensor import ParticuleSensor
from influxdb import InfluxDBClient

# TODO signal catcher for shutdown
# TODO env variable instead for easy config within docker
DB_NAME = 'luftdata'


class AirStation:
    def __init__(self):

        # TODO change hostname when moving this code to docker container
        self.db_client = InfluxDBClient(host='localhost', port=8086)
        db_list = self.db_client.get_list_database()
        print(db_list)
        self.db_exists = False
        for db in db_list:
            if db["name"] == DB_NAME:
                self.db_exists = True

        if not self.db_exists:
            print("Database does not exist, will create it")
            self.db_client.create_database(dbname=DB_NAME)
            self.db_client.create_retention_policy(name="Retention_policy",
                                                   duration="52w",
                                                   replication="1",
                                                   database=DB_NAME,
                                                   shard_duration="1w")

        self.db_client.switch_database(DB_NAME)

        self._particule_sensor = ParticuleSensor(self.db_client)

    def start_station(self):
        self._particule_sensor.read_port()


if __name__ == '__main__':
    print("Started air station")
    station = AirStation()
    station.start_station()
