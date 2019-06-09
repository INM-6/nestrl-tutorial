#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import time
import zmq


ctx = zmq.Context()

sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:5557')
sub.setsockopt(zmq.SUBSCRIBE, b'')

# set timeout to avoid getting stuck when sender is not available
sub.RCVTIMEO = 2000  # millisecond

t_max = 3.  # seconds
dt = 0.01  # seconds

print('start receiving')

times = []
history = []
for t in np.arange(0, t_max, dt):
    try:
        msg = sub.recv_json()
    except zmq.error.Again:  # timeout, try again
        continue

    print('recv', msg)
    times.append(t * 1e3)
    history.append(msg[0]['value'])
    time.sleep(dt)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Low-pass filtered spikes (1/s)')

ax.plot(times, history)
fig.savefig('zmq_output.png', dpi=300)

print('stop receiving')
