# LANCEMENT AU BOOT DU PI 
# vi /etc/rc.local
# python3 /home/pi/bin/tempServer.py &

from http.server import HTTPServer, BaseHTTPRequestHandler

import serial
import time
import logging
import requests
from datetime import datetime
from influxdb import InfluxDBClient
from io import BytesIO
import simplejson



# création du logguer
logging.basicConfig(filename='/var/log/tempServer.log', level=logging.INFO, format='%(asctime)s %(message)s')

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        logging.info("GET request")
        self.wfile.write(b'Get request succeed')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        
        data = simplejson.loads(body)
        add_measures('temperature', float(data['temperature']), data['location']);
        add_measures('humidity', float(data['humidity']), data['location']);
        
        response.write(b'This is POST request.Received: ')
        logging.info("request from %s", data['location'])
        print ("request ", body)
        response.write(body)
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('192.168.1.21', 5000), SimpleHTTPRequestHandler)


def add_measures(key, value, location):
    points = []
    point = {
                "measurement": key,
                "tags": {
                    "host": "ESP8266",
                    "location": location
                },
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "value": value
                }
            }
    points.append(point)
    client.write_points(points)


logging.info("TempServer starting..")


# connexion a la base de données InfluxDB
client = InfluxDBClient('localhost', 8086)
db = "homedata"
connected = False
while not connected:
    try:
        print ("Database %s exists?", db)
        if not {'name': db} in client.get_list_database():
            print ("Database %s creation..", db)
            client.create_database(db)
            print ("Database %s created!", db)
        client.switch_database(db)
        print ("Connected to ", db)
    except requests.exceptions.ConnectionError:
        print ('InfluxDB is not reachable. Waiting 5 seconds to retry.')
        time.sleep(5)
    else:
        connected = True




httpd.serve_forever()