import board
import busio
from digitalio import DigitalInOut
from adafruit_bluefruitspi import BluefruitSPI

test_data = []

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



def connect_ble():
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

def read_ble():
    if not bluefruit.connected:
        return
    # OK we're still connected, see if we have any data waiting
    resp = bluefruit.uart_rx()
    if not resp:
        return  # nothin'
    #print("Read %d bytes: %s" % (len(resp), resp))
    data_string = ''.join([chr(b) for b in resp])
    print(data_string, end="")
    return data_string

def write_ble(msg):
    # Now write it!
    global test_data
    print(test_data)
    if isinstance(msg,list):
        m= {"data":{"t":0,"v":0,"i":0}}
        for i in test_data:
            m["data"]["t"]+=i["t"]
            m["data"]["v"]+=i["v"]
            m["data"]["i"]+=i["i"]
        m["data"]["t"]=m["data"]["t"]/len(test_data)
        m["data"]["v"]=m["data"]["v"]/len(test_data)
        m["data"]["i"]=m["data"]["i"]/len(test_data)
        m["done"]=test_data[-1].get("done",False)
        msg = str(m) + '$'
        bluefruit.uart_tx(str.encode(msg))
        test_data=[]
    else:
        msg = str(msg) + '$'
        bluefruit.uart_tx(str.encode(msg))
