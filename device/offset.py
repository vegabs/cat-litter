import time

try:
    from potentiostat import Potentiostat
except ImportError:
    class Potentiostat:
        def __init__(self):
            self.connected = False
            self.voltage = 0.0
            self.current = 0.0
            self.vpow = 3.3

from potentiostat import clamp

def num_to_range(num, inMin, inMax, outMin, outMax):
    return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

def get_current_with_sleep(pstat, voltage, sleep_dt):
    pstat.offset = clamp(voltage,clamp(pstat.voltage,-1.64,-0.015), clamp(pstat.voltage,0.015,1.64))
    time.sleep(sleep_dt)
    rsp = pstat.current
    return rsp

def offsetV(pstat, voltage, oc = 0):
    step = 0.05
    sleep_dt = 0.02
    direction = None

    current = get_current_with_sleep(pstat, voltage, sleep_dt)

    if (round(current,10) < round(oc,10)):
        voltage += step
        current = get_current_with_sleep(pstat, voltage, sleep_dt)
        direction = "up"
    elif (round(current,10) > round(oc,10)):
        voltage -= step
        current = get_current_with_sleep(pstat, voltage, sleep_dt)
        direction = "down"
    else:
        voltage = round((voltage*0.5),3)
        current = get_current_with_sleep(pstat, voltage, sleep_dt)
        direction = "zero"

    print(' offset v: {:1.3e}, i: {:1.3e}'.format(voltage, current),direction)
    return voltage
