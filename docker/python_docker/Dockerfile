FROM python:latest
ADD src /src
RUN pip install influxdb pyserial

CMD [ "python", "-u", "./src/air_station.py" ]