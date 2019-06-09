#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import sys

from mpi4py import MPI
comm = MPI.COMM_WORLD

simtime = 3000.

# setup and simulate

nest.ResetKernel()

nest.SetKernelStatus({'resolution': 1.0})  # TODO fix resolution issue

music_rate_in = nest.Create('music_rate_in_proxy', 1, {'port_name': 'in'})
music_rate_out = nest.Create('music_rate_out_proxy', 1, {'port_name': 'out'})
neuron = nest.Create('lin_rate_ipn', 1, {'sigma': 0.})
m = nest.Create('multimeter', 1, {'record_from': ['rate']})

nest.Connect(music_rate_in, neuron, syn_spec={'model': 'rate_connection_instantaneous'})
nest.Connect(neuron, music_rate_out, syn_spec={'model': 'rate_connection_instantaneous'})
nest.Connect(m, neuron)

comm.Barrier()  # necessary to synchronize with MUSIC
nest.Simulate(simtime)

# plot results

events = nest.GetStatus(m, 'events')[0]

fig = plt.figure()

ax = fig.add_subplot(111)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Rate (1/s)')
ax.set_xlim([0., simtime])

ax.plot(events['times'], events['rate'], 'k')

fig.savefig('nest_output_rate.png', dpi=300)
