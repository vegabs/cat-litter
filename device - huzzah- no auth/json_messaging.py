import sys
import json
import supervisor

class Receiver:

    msg_to_self = {}

    def __init__(self):
        self.buffer = []
        self.error_flag = False
        self.error_count = 0

    @property
    def error(self):
        return self.error_flag

    def update(self):
        new_message = False
        while supervisor.runtime.serial_bytes_available:
            byte = sys.stdin.read(1)
            if byte != '\n':
                self.buffer.append(byte)
            else:
                message_str = ''.join(self.buffer)
                self.buffer = []
                new_message = True
                break
        message_dict = {}
        self.error_flag = False
        if new_message:
            try:
                message_dict = json.loads(message_str)
            except ValueError:
                self.error_flag = True
                self.error_count += 1
        elif Receiver.msg_to_self:
            message_dict = Receiver.msg_to_self
            Receiver.msg_to_self = {}
        return message_dict



def send(msg):
    print(json.dumps(msg))

def send_to_self(msg):
    if isinstance(msg, str) and msg[0] == '{':
        try:
            msgD = json.loads(msg)
            Receiver.msg_to_self = msgD
        except ValueError:
            print("Message not correct. Be sure to use double quotation marks! Not '' these.")
    else:
        Receiver.msg_to_self = msg
