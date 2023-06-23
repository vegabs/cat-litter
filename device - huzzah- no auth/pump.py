try:
    from time import monotonic as time_in_secs
except ImportError:
    from time import time as time_in_secs

import board
import digitalio

class Pump:

    switch = digitalio.DigitalInOut(board.D12)
    switch.direction = digitalio.Direction.OUTPUT

    def __init__(self, duration):
        self.done = False
        self.duration = duration
        self.sample_period = 1.0/16
        self.t_now = time_in_secs()
        self.t_start = self.t_now
        self.t_last_sample = self.t_now
        self.t_next_sample = self.t_now

    def __del__(self):
        self.cleanup()

    def setup(self):
        self.done = False

    def cleanup(self):
        self.switch.value = False

    def update(self):
        self.done = False
        self.t_now = time_in_secs()
        self.t_last_sample = self.t_now

        if self.t_now >= self.t_start + self.duration:
              self.done = True

        if (self.t_now >= self.t_next_sample) or self.done:
            self.t_next_sample = self.t_now + self.sample_period
            #print(self.t_now)
            if self.done:
                self.switch.value = False
            else:
                self.switch.value = True
                print('pumping')
