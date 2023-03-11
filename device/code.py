import time
import command
import scheduler
import potentiostat
import cyclic_test
import ocp_test
import pump

try:
    from json_messaging import send
except ImportError:
    import json
    def send(msg):
        print('send: {}'.format(json.dumps(msg)))

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
commander.msg = parameters

while True:
    job_scheduler.update()
    # if (not bool(job_scheduler.table)):
    #     print("empty")
