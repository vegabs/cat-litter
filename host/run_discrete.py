import matplotlib.pyplot as plt
from potentiostat import  Potentiostat

output_file = 'data_discrete.txt'

param = {
        'setpoint_voltage': 1.0,
        'max_voltage'   :  1.5,
        'min_voltage'   : -1.5,
        'scan_rate'     :  0.20,
        'start_voltage' : 'setpoint_voltage',
        'sample_rate'   : 200,
        'cycles'        : 10,
        'duration'      : 10.0
        }

pstat = Potentiostat('COM4')
pstat.range('1000uA')
pstat.averaging(50)
pstat.offset(0.0)

pstat.connected(True)
t, v, i = pstat.run_test('discrete', param)
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

plt.figure(2)
plt.plot(v,i)
plt.xlabel('(V)')
plt.ylabel('(uA)')
plt.grid(True)
plt.show()

with open(output_file,'w') as f:
    for (tt,vv,ii) in zip(t,v,i):
        f.write('{}, {}, {}\n'.format(tt,vv,ii))

















