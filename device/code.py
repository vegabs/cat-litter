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

import board
import busio
from digitalio import DigitalInOut
from adafruit_bluefruitspi import BluefruitSPI

spi_bus = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.D6)
irq = DigitalInOut(board.D5)
rst = DigitalInOut(board.D9)
bluefruit = BluefruitSPI(spi_bus, cs, irq, rst, debug=False)

# Initialize the device and perform a factory reset
print("Initializing the Bluefruit LE SPI Friend module")
bluefruit.init()
bluefruit.command_check_OK(b'AT+FACTORYRESET', delay=1)

# Print the response to 'ATI' (info request) as a string
print(str(bluefruit.command_check_OK(b'ATI'), 'utf-8'))

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
print("Waiting for a connection to Bluefruit LE Connect ...")
# Wait for a connection ...
dotcount = 0
while not bluefruit.connected:
    print(".", end="")
    dotcount = (dotcount + 1) % 80
    if dotcount == 79:
        print("")

# Once connected, check for incoming BLE UART data
print("\n *Connected!*")

while True:
    job_scheduler.update()

    if len(job_scheduler.table) <= 1:
        cat_sensor.update()

        # Check our connection status every 3 seconds
        if time_in_secs()%10:
            if not bluefruit.connected:
                continue
            # OK we're still connected, see if we have any data waiting
            resp = bluefruit.uart_rx()
            if not resp:
                continue  # nothin'
            print("Read %d bytes: %s" % (len(resp), resp))
            data_string = ''.join([chr(b) for b in resp])
            print(data_string, end="")
            commander.msg = data_string
            # Now write it!
            # print("Writing reverse...")
            # send = []
            # for i in range(len(resp), 0, -1):
            #     send.append(resp[i-1])
            # print(bytes(send))
            # bluefruit.uart_tx(bytes(send))
