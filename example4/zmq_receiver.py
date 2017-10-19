#!/usr/bin/env python

import json
import time
import zmq


ctx = zmq.Context()

sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:5555')
sub.setsockopt(zmq.SUBSCRIBE, b'')
sub.RCVTIMEO = 1000  # set timeout to avoid getting stuck when sender is not available

t_max = 10.
t = 0
dt = 0.01

print('start receiving')

while t < t_max:

    try:
        msg = sub.recv_json()
    except zmq.error.Again:  # timeout, try again
        continue

    print(msg)
    time.sleep(dt)

    t += dt

print('stop sending')
