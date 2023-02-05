from http.server import BaseHTTPRequestHandler, HTTPServer
import paho.mqtt.client as mqtt
import time
import sys
import requests
import configparser

#test command wget -qO- "http://localhost:8080/weatherstation/updateweatherstation.php?ID=55&PASSWORD=asdfghjkl&action=updateraww&realtime=1&rtfreq=5&dateutc=now&baromin=29.91&tempf=74.3&dewptf=41.9&humidity=31&windspeedmph=1.7&windgustmph=1.7&winddir=0&rainin=0.0&dailyrainin=0.0&solarradiation=0.23&UV=0.0&indoortempf=76.8&indoorhumidity=26&soiltempf=73.2&soilmoisture=35" &> /dev/null

#test run python3 sencor-sws-12500-ha.py <ip> 1883 <mqtt_user> <mqtt_pass> sencor_sws_12500 8080 1

config = configparser.ConfigParser()
config.read('db.ini')

mqtt_ip = config['mqtt']['ip']
mqtt_port = config['mqtt']['port']
mqtt_user = config['mqtt']['user']
mqtt_pass = config['mqtt']['pass']
sensor_name_prefix = config['sensor']['prefix']
http_port = config['http']['port']
wunderground = config['wunderground']['proxy']


client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_pass)
client.connect(mqtt_ip, int(mqtt_port), 60)
client.loop_start()

init = True

sensors_config ={
'baromin' : '"device_class" : "atmospheric_pressure", "state_class" : "measurement", "unit_of_measurement": "mbar"',
'tempf' : '"device_class" : "temperature", "state_class" : "measurement", "unit_of_measurement": "°C"',
'dewptf': '"device_class" : "temperature", "state_class" :"measurement", "unit_of_measurement": "°C"',
'humidity': '"device_class" : "humidity","state_class" :"measurement", "unit_of_measurement": "%"',
'windspeedmph' : '"device_class" : "wind_speed","state_class" :"measurement", "unit_of_measurement": "m/s"',
'windgustmph' : '"device_class" : "wind_speed","state_class" :"measurement", "unit_of_measurement": "m/s"',
'winddir' : '"device_class" : "None"',
'rainin' : '"device_class" : "distance","state_class" :"measurement", "unit_of_measurement": "mm"',
'dailyrainin' : '"device_class" : "distance","state_class" :"measurement", "unit_of_measurement": "mm"',
'solarradiation' : '"device_class" : "irradiance","state_class" :"measurement", "unit_of_measurement": "w/m2"',
'UV' : ' "device_class" : "None","state_class" :"measurement"',
'indoortempf' : '"device_class" : "temperature", "state_class" : "measurement", "unit_of_measurement": "°C"',
'indoorhumidity' : '"device_class" : "humidity","state_class" :"measurement", "unit_of_measurement": "%"',
'soiltempf' : '"device_class" : "temperature", "state_class" : "measurement", "unit_of_measurement": "°C"',
'soilmoisture' : ' "device_class" : "humidity","state_class" :"measurement", "unit_of_measurement": "%"'
}

sensors_units_conversion = {
'baromin' : lambda x : round(float(x) * 33.86,2),
'tempf' : lambda x : round((float(x)-32) / 1.8,2),
'dewptf' : lambda x : round((float(x)-32) / 1.8,2),
'windspeedmph' : lambda x : round(float(x) * 447.04,1),
'windgustmph' : lambda x : round(float(x) * 447.04,1),
'winddir' : lambda x : '"{}"'.format(['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW','N'][int((float(x)+11.25)/22.5)]),
'indoortempf' : lambda x : round((float(x)-32) / 1.8,2),
'soiltempf' : lambda x : round((float(x)-32) / 1.8,2)
}

class MyServer(BaseHTTPRequestHandler):

	def get_config(self, sensor):
		config_data = '{{"name" : "{0}_{1}", "state_topic" : "homeassistant/sensor/{0}/state", "value_template": "{{{{ value_json.{1}}}}}", {2}}}'.format(sensor_name_prefix, sensor, sensors_config[sensor])
		return config_data
	
	def do_GET(self):
		global init
		send_data = ""
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		url = self.path.split('?')

		if url[0] == "/weatherstation/updateweatherstation.php":
			data = url[1].split('&')
			for x in data:
				sensor = x.split('=')
				if sensor[0] in sensors_config:
					if init:
						client.publish("homeassistant/sensor/{}/config".format(sensor_name_prefix + sensor[0]), self.get_config(sensor[0]))
					if 	sensor[0] in sensors_units_conversion:					
						send_data += '"{}":{},'.format(sensor[0],sensors_units_conversion[sensor[0]](sensor[1]))
					else:
						send_data += '"{}":{},'.format(sensor[0],sensor[1])											
			client.publish("homeassistant/sensor/{}/state".format(sensor_name_prefix), "{" + send_data[:-1] + "}")
			if wunderground:
				requests.get("https://pws-ingest-use1-01.sun.weather.com/weatherstation/updateweatherstation.php?"+url[1])
		init = False

if __name__ == "__main__":
    webServer = HTTPServer(('', int(http_port)), MyServer)
    print("Server started http://%s:%s" % ('*', http_port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
    client.loop_stop()
