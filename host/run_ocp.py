import matplotlib.pyplot as plt
from potentiostat import  Potentiostat
import serial.tools.list_ports

if __name__ == '__main__':
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "USB" in p.description:
            PORT=p.name

output_file = 'data_ocp.txt'

param = {
        'setpoint_voltage': 0.000001,
        'scan_rate'     :  0.20,
        'sample_rate'   : 16.0,
        'duration'      : 7.0
        }

pstat = Potentiostat(PORT)
pstat.range('1000uA')
pstat.averaging(16)
pstat.offset(0.0)

pstat.connected(False)
t, v, i = pstat.run_test('OCP', param)
pstat.connected(False)

i = 1.0e6*i # convert to uA

plt.figure(1)
plt.subplot(2,1,1)
plt.plot(t,v)
plt.ylabel('(V)')
plt.grid(True)
plt.subplot(2,1,2)
plt.plot(t,i)
plt.ylabel('(uA)')
plt.xlabel('time (s)')
plt.grid(True)
plt.show()


with open(output_file,'w') as f:
    for (tt,vv,ii) in zip(t,v,i):
        f.write('{}, {}, {}\n'.format(tt,vv,ii))
