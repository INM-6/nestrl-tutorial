#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import sys

from mpi4py import MPI
comm = MPI.COMM_WORLD

simtime = 2000.

# setup and simulate

nest.ResetKernel()

nest.SetKernelStatus({'overwrite_files': True, 'resolution': 1.0})

music_in = nest.Create('music_rate_in_proxy', 1, {'port_name': 'in'})

neuron = nest.Create('lin_rate_ipn', 1, {'mu': 1., 'sigma': 0.})

m = nest.Create('multimeter', 1, {'record_from': ['rate']})

nest.Connect(music_in, neuron, syn_spec={'model': 'rate_connection_instantaneous', 'weight': 1.})
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
