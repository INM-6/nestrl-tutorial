#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import sys

from mpi4py import MPI
comm = MPI.COMM_WORLD

simtime = 1500.

# setup and simulate

nest.ResetKernel()

music_in_proxy = nest.Create('music_event_in_proxy', 1, {'port_name': 'in'})
neuron = nest.Create('iaf_psc_exp')
sd = nest.Create('spike_detector')
mv = nest.Create('multimeter', 1, {'record_from': ['V_m']})

nest.Connect(music_in_proxy, neuron, syn_spec={'weight': 120.})
nest.Connect(neuron, sd)
nest.Connect(mv, neuron)

comm.Barrier()  # necessary to synchronize with MUSIC

nest.Simulate(simtime)

# plot results

spikes = nest.GetStatus(sd, 'events')[0]
vm = nest.GetStatus(mv, 'events')[0]

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel('Time (ms)')
ax.set_ylabel('Membrane potential (mV)')
ax.set_xlim([0., simtime])
ax.set_ylim([-70., -45.])

ax.plot(spikes['times'], [-48.] * len(spikes['times']), 'bo', label='Spikes', markeredgewidth=0, markersize=3)
ax.plot(vm['times'], vm['V_m'], 'k', label='Free membrane potential')

ax.legend(loc='upper right')

fig.savefig('nest_output.png', dpi=300)
