import time
import command
import scheduler
import potentiostat
import cyclic_test
import ocp_test

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
                                'duration'      : 7.0
                                }
                        }
                }
job_scheduler = scheduler.Scheduler()
job_scheduler.add('command', command.Handler(job_scheduler, pstat, parameters))

while True:
    job_scheduler.update()
