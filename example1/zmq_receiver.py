#!/usr/bin/env python

import json
import time
import zmq


ctx = zmq.Context()

sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:5557')
sub.setsockopt(zmq.SUBSCRIBE, b'')
sub.RCVTIMEO = 1000  # set timeout to avoid getting stuck when sender is not available

t_max = 10.
t = 0
dt = 0.01

print('start receiving')

while t < t_max:

    try:
        msg = json.loads(sub.recv())
    except zmq.error.Again:  # timeout, try again, but increase time
        t += dt
        continue

    print('recv', msg)
    time.sleep(dt)

    t += dt

print('stop sending')
