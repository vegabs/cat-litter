from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

def connect_ble():
    ble.start_advertising(advertisement)
    print("Waiting to connect")
    while not ble.connected:
        pass
    print("Connected")

def read_ble():
    if not ble.connected:
        return
    if ble.connected:
        s = uart.readline()
        if s:
            try:
                result = str(s+"yay")
                commander.msg=s
            except Exception as e:
                result = str(s+"yayexcept")

def write_ble(msg):
    # Now write it!
    msg = str(msg) + '$'
    print(str.encode(msg))
    uart.write(str.encode(msg))
