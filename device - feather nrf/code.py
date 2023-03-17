try:
    from time import monotonic as time_in_secs
except ImportError:
    from time import time as time_in_secs
import command
import scheduler
import potentiostat
import cyclic_test
import ocp_test
import pump
import tof
try:
    from json_messaging import send
except ImportError:
    import json
    def send(msg):
        print('send: {}'.format(json.dumps(msg)))
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import board
import busio

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

ble.start_advertising(advertisement)
print("Waiting to connect")
while not ble.connected:
    pass
print("Connected")
pstat = potentiostat.Potentiostat(current_range='1000uA')
parameters = {
                'range':'1000uA',
                'averaging':16,
                'offset':0.0,
                'connected':False,
                'test': {
                        'name': 'OCP',
                        'param': {
                                'setpoint_voltage': 0.000001,
                                'scan_rate'     :  0.20,
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

    if len(job_scheduler.table) <= 1:
        cat_sensor.update()

    if ble.connected:
        s = uart.readline()
        if s:
            try:
                result = str(s+"yay")
                commander.msg=s
            except Exception as e:
                result = str(s+"yayexcept")
            uart.write(result)
