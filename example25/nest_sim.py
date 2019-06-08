#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import sys

from mpi4py import MPI
comm = MPI.COMM_WORLD

simtime = 3000.

# setup and simulate

nest.ResetKernel()

music_event_in = nest.Create('music_event_in_proxy', 1, {'port_name': 'in'})
music_event_out = nest.Create('music_event_out_proxy', 1, {'port_name': 'out'})
neuron = nest.Create('iaf_psc_exp')
sd = nest.Create('spike_detector')
m = nest.Create('multimeter', 1, {'record_from': ['V_m']})

# set up dummy neuron to record low-pass filtered spikes
dummy_neuron = nest.Create('iaf_psc_delta', 1, {'V_th': 1e3, 'tau_m': 1000., 'E_L': 0., 'V_m': 0.})
m_dummy = nest.Create('multimeter', 1, {'record_from': ['V_m']})

nest.Connect(music_event_in, neuron, syn_spec={'weight': 120.})
nest.Connect(neuron, sd)
nest.Connect(m, neuron)
nest.Connect(neuron, music_event_out)

nest.Connect(neuron, dummy_neuron, syn_spec={'weight': 1.})
nest.Connect(m_dummy, dummy_neuron)

comm.Barrier()  # necessary to synchronize with MUSIC
nest.Simulate(simtime)

# plot results

spikes = nest.GetStatus(sd, 'events')[0]
vm = nest.GetStatus(m, 'events')[0]
vm_dummy = nest.GetStatus(m_dummy, 'events')[0]

fig = plt.figure()

ax = fig.add_axes([0.15, 0.15, 0.3, 0.8])
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Membrane potential (mV)')
ax.set_xlim([0., simtime])
ax.set_ylim([-70., -45.])

ax_dummy = fig.add_axes([0.6, 0.15, 0.30, 0.8])
ax_dummy.set_xlabel('Time (ms)')
ax_dummy.set_ylabel('Low-pass filtered spikes (1/s)')

ax.plot(spikes['times'], [-48.] * len(spikes['times']), ls='', marker='o', label='Spikes', markeredgewidth=0, markersize=3)
ax.plot(vm['times'], vm['V_m'], 'k', label='Membrane potential (mV)')
ax.legend(loc='upper right', fontsize=8)

ax_dummy.plot(vm_dummy['times'], vm_dummy['V_m'])

fig.savefig('nest_output.png', dpi=300)
