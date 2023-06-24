try:
    from time import monotonic as time_in_secs
except ImportError:
    from time import time as time_in_secs

import board
import busio
import adafruit_vl53l0x

from json_messaging import send_to_self

class ToF:

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_vl53l0x.VL53L0X(i2c)
        self.sensed = False
        self.sensed_t = 999999999
        self.get_ready = False


    def cleanup(self):
        self.sensed = False
        self.sensed_t = 999999999
        self.get_ready = False

    def sensing(self):
        if self.sensed and self.sensor.range < 400:
            pass
        elif not self.sensed and self.sensor.range < 400:
            self.sensed = True
            self.sensed_t = time_in_secs()
        else:
            self.sensed = False
            self.sensed_t = 999999999

    def update(self):
        self.sensing()
        sensed_dt=0
        if self.sensed:
            sensed_dt = time_in_secs() - self.sensed_t
            print(sensed_dt)
        if sensed_dt > 5:
            self.get_ready = True
            print('ready')
        if self.get_ready and not self.sensed:
            print('ca test')
            send_to_self({'default ca'})
            self.get_ready = False
