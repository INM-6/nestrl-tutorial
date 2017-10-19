#!/usr/bin/env python

import numpy as np
import time
import zmq


ctx = zmq.Context()

sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:5556')
sub.setsockopt(zmq.SUBSCRIBE, b'')

# set timeout to avoid getting stuck when sender is not available
sub.RCVTIMEO = 1000  # millisecond

t_max = 10.  # seconds
dt = 0.01  # seconds

print('start receiving')

for t in np.arange(0, t_max, dt):
    try:
        msg = sub.recv_json()
    except zmq.error.Again:  # timeout, try again
        continue

    print('recv', msg)
    time.sleep(dt)

print('stop receiving')
