# Air-station

Simple air station application collecting data, saving them in an 
InfluxDB and displayed using Grafana.

## Installation

To install simply execute 
  `docker-compose up --build -d`
  
 You will need to give read permission to the serial port of your sensor.
 If sensor path is not listed as /dev/ttyUSB0, update it in the docker-compose.yml 
 file
 
 
 This project is based on: 
 [Luftdata](https://luftdata.se/)