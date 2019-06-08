#!/usr/bin/env python

import math
import numpy as np
import time
import zmq


def GymObservation(low, high, value):
    """Converts value in range low high to the format of a GymObservation.

    """
    return [{'min': low, 'max': high, 'value': value, 'ts': time.time()}]


ctx = zmq.Context()

pub = ctx.socket(zmq.PUB)
pub.bind('tcp://*:5556')

t_max = 10.
dt = 0.01

print('start sending')

for t in np.arange(0, t_max, dt):
    msg = GymObservation(-1., 1., math.sin(2 * math.pi * t))
    print('send', msg)
    pub.send_json(msg)
    time.sleep(dt)

print('stop sending')
