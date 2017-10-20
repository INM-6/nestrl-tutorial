#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import sys

from mpi4py import MPI
comm = MPI.COMM_WORLD

simtime = 2000.
tau_m = 1.
tau_syn = 50.

# setup and simulate

nest.ResetKernel()

nest.SetKernelStatus({'overwrite_files': True, 'resolution': 1.})

music_in_proxy = nest.Create('music_event_in_proxy', 1, {'port_name': 'in'})

neuron = nest.Create('iaf_psc_exp', 1, {'E_L': -65., 'V_th': -60., 'tau_m': tau_m, 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn})
dummy_neuron = nest.Create('iaf_psc_exp', 1, {'E_L': -65., 'V_th': 0., 'tau_m': tau_m, 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn})

sd = nest.Create('spike_detector')

mv = nest.Create('multimeter', 1, {'record_from': ['V_m']})

nest.Connect(music_in_proxy, neuron, syn_spec={'weight': 200.})
nest.Connect(music_in_proxy, dummy_neuron, syn_spec={'weight': 200.})

nest.Connect(neuron, sd)

nest.Connect(mv, dummy_neuron)

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
ax.set_ylim([-65., -50.])

ax.plot(spikes['times'], [-55.] * len(spikes['times']), 'bo', label='Spikes', markeredgewidth=0, markersize=2)
ax.plot(vm['times'], vm['V_m'], 'k', label='Membrane potential')

ax.legend(loc='upper right')

fig.savefig('nest_output.png', dpi=300)
