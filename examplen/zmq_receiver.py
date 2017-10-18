#!/usr/bin/env python

import json
import time
import zmq


ctx = zmq.Context()

sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:5556')
sub.setsockopt(zmq.SUBSCRIBE, b'')

t_max = 10.
t = 0
dt = 0.01

print('start receiving')

while t < t_max:
    msg = json.loads(sub.recv())
    print(msg)
    time.sleep(dt)

    t += dt

print('stop sending')
