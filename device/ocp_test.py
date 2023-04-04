try:
    from time import monotonic as time_in_secs
except ImportError:
    from time import time as time_in_secs

try:
    from potentiostat import Potentiostat
except ImportError:
    class Potentiostat:
        def __init__(self):
            self.connected = False
            self.voltage = 0.0
            self.current = 0.0
            self.vpow = 3.3

try:
    from json_messaging import send
except ImportError:
    import json
    def send(msg):
        print('send: {}'.format(json.dumps(msg)))

from json_messaging import send_to_self
import ble_messaging

from offset import offsetV

class OCPTest:
    MAX_SAMPLE_RATE = 200.0

    def __init__(self,pstat,param):
        ble_messaging.write_ble("test starting")
        self.param = {}
        self.done = False
        self.pstat = pstat
        self.t_start = 0.0
        self.t_now = 0.0
        self.t_last_sample = 0.0
        self.t_next_sample = 0.0
        self.voltage_range_max =  0.5*self.pstat.vpow
        self.voltage_range_min = -0.5*self.pstat.vpow
        self.sample_period = 1.0
        ok, msg = self.extract_param(param)
        if ok:
            self.setup()
        else:
            msg_dict = {'error': msg}
            send(msg_dict)
            self.done = True
            self.cleanup()
        self.sample_period = 1.0/self.param['sample_rate']


    def __del__(self):
        self.cleanup()


    @property
    def voltage(self):
        return self.pstat.voltage


    @voltage.setter
    def voltage(self,v):
        self.pstat.voltage = v


    @property
    def current(self):
        return self.pstat.current

    @property
    def ref_voltage(self):
        return self.pstat.ref_voltage


    @property
    def elapsed_time(self):
        return self.t_now - self.t_start


    def update(self):
        self.t_now = time_in_secs()
        self.t_last_sample = self.t_now


        if self.t_now >= self.t_start + self.param['duration']:
            self.done = True

        if (self.t_now >= self.t_next_sample) or self.done:
            current_uA = 1.0e6*self.current
            ble_messaging.test_data.append({'t': self.elapsed_time, 'v': self.ref_voltage, 'i': current_uA})

            if self.done:
                ble_messaging.test_data[-1]["done"]=True
                ble_messaging.write_ble(ble_messaging.test_data)
                send_to_self({'pump':3.0})
            if (len(ble_messaging.test_data) >= 16):
                offsetV(self.pstat,self.pstat.offset,self.oc)
                self.oc = self.current
                ble_messaging.write_ble(ble_messaging.test_data)
            #write_ble(data_dict)
            #send(data_dict)
            self.t_next_sample = self.t_now + self.sample_period


    def setup(self):
        ble_messaging.test_data = []
        self.t_now = time_in_secs()
        self.t_start = self.t_now
        self.t_last_sample = self.t_now
        self.t_next_sample = self.t_now
        self.oc = offsetV(self.pstat, self.param['setpoint_voltage'])
        self.voltage = self.param['setpoint_voltage']
        self.done = False
        self.pstat.connected = False



    def cleanup(self):
        self.pstat.connected = False
        self.voltage = 0.0


    def extract_param(self,param):

        # Check that we have all required items in param
        expected_keys = [
                'sample_rate',
                'duration',
                'setpoint_voltage'
                ]

        param_tmp = {}
        for key in expected_keys:
            try:
                param_tmp[key] = param[key]
            except KeyError:
                return False, 'missing param {}'.format(key)

        # Check that float values are of correct type
        float_keys  = [
                'sample_rate',
                'duration',
                'setpoint_voltage'
                ]
        for key in float_keys:
            try:
                param_tmp[key] = float(param_tmp[key])
            except(ValueError, TypeError):
                return False, '{} must be float'.format(key)

        positive_keys = [
                'sample_rate',
                'duration'
                ]
        for key in positive_keys:
            if param_tmp[key] <= 0:
                return False, '{} must be > 0'.format(key)

        # Check that voltages are within range and that min < max voltage
        for key in ['setpoint_voltage']:
            if param_tmp[key] > self.voltage_range_max:
                return False, '{} > voltage_range_max'.format(key)
            if param_tmp[key] < self.voltage_range_min:
                return False, '{} < voltage_range_min'.format(key)

        # Check that sample rate is less or equal than maximum allowed sample rate
        if param_tmp['sample_rate'] > self.MAX_SAMPLE_RATE:
            return False, 'sample_rate must be <= {}'.format(self.MAX_SAMPLE_RATE)

        self.param = param_tmp
        return True, ''
