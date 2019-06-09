#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import numpy as np

from mpi4py import MPI
comm = MPI.COMM_WORLD


simtime = 5000.  # needs to match the stoptime (here in ms) defined in the music config

# setup and simulate

nest.ResetKernel()

nest.SetKernelStatus({'resolution': 1.0})  # TODO fix resolution issue

music_rate_in = nest.Create('music_rate_in_proxy', 1, {'port_name': 'in'})

neuron_left = nest.Create('lin_rate_ipn', 1, {'mu': 0., 'sigma': 0.})
neuron_right = nest.Create('lin_rate_ipn', 1, {'mu': 0., 'sigma': 0.})

m_left = nest.Create('multimeter', 1, {'record_from': ['rate']})
m_right = nest.Create('multimeter', 1, {'record_from': ['rate']})

nest.Connect(music_rate_in, neuron_left, syn_spec={'model': 'rate_connection_instantaneous', 'weight': 1.})
nest.Connect(music_rate_in, neuron_right, syn_spec={'model': 'rate_connection_instantaneous', 'weight': -1.})

nest.Connect(m_left, neuron_left)
nest.Connect(m_right, neuron_right)

comm.Barrier()  # necessary to synchronize with MUSIC
nest.Simulate(simtime)

# plot results

events_left = nest.GetStatus(m_left, 'events')[0]
events_right = nest.GetStatus(m_right, 'events')[0]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel('Time (ms)')
ax.set_xlim([0., simtime])

ax.plot(events_left['times'], events_left['rate'], label='left')
ax.plot(events_right['times'], events_right['rate'], label='right')
ax.legend(fontsize=8)

fig.savefig('nest_output_rate.png', dpi=300)
