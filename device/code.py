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
from json_messaging import send_to_self
import ble_messaging

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
ble_messaging.connect_ble()

while True:
    job_scheduler.update()

    if len(job_scheduler.table) <= 1:
        cat_sensor.update()

        # Check our connection status every 3 seconds
        if time_in_secs()%10:
            ble_msg = ble_messaging.read_ble()
            if ble_msg:
                send_to_self(ble_msg)

            #simple example write
            # writer= {"data": {"t": 0, "v": 0, "i": 0}}
            # ble_messaging.write_ble(writer)
