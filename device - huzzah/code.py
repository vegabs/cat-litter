import time
import board
import busio as io
import pyrebase
import os
import ipaddress
import wifi
import socketpool
try:
    from time import monotonic as time_in_secs
except ImportError:
    from time import time as time_in_secs
import command
import scheduler
import potentiostat
import tof
try:
    from json_messaging import send
except ImportError:
    import json
    def send(msg):
        print('send: {}'.format(json.dumps(msg)))
from json_messaging import send_to_self

print()
print("Connecting to WiFi")

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

print("Connected to WiFi")
#pool = socketpool.SocketPool(wifi.radio)

#  prints MAC address to REPL
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

#  prints IP address to REPL
print("My IP address is", wifi.radio.ipv4_address)

# no auth
config = {
  "apiKey": os.getenv('APIKEY'),
  "authDomain": "circat-purrtentio.firebaseapp.com",
  "databaseURL": "https://circat-purrtentio-default-rtdb.firebaseio.com",
  "storageBucket": "circat-purrtentio.appspot.com"
}

# email account
#config["credentials"] = {"email": os.getenv("EMAIL"), "password": os.getenv("PASSWORD")}

# service account
#config["credentials"] = os.getenv("CRED")


pyrebase.initialize_app(config)

print("----------------------------------------")
print()

pstat = potentiostat.Potentiostat(current_range='1000uA')
parameters = {
                'range':'1000uA',
                'averaging':16,
                'offset':0.0,
                'connected':False,
                'test': {
                        'name': 'OCP',
                        'param': {
                                'setpoint_voltage': 0.0,
                                'sample_rate'   : 16.0,
                                'duration'      : 4.0
                                }
                        }
                }
job_scheduler = scheduler.Scheduler()
commander = command.Handler(job_scheduler, pstat)
job_scheduler.add('command', commander)
#commander.msg = parameters
cat_sensor = tof.ToF()

while True:
    job_scheduler.update()

    #if time_in_secs()%80000:
        #print("main", ble_messaging.test_data)
    if len(job_scheduler.table) <= 1:
        cat_sensor.update()

        # Check our connection status every 3 seconds
        if round(time_in_secs()%10):
            wifi_msg = pyrebase.db.get()
            if wifi_msg:
                # send_to_self(wifi_msg)
                print(wifi_msg)
