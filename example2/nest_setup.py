#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import sys

simtime = float(sys.argv[1]) * 1e3  # convert to milliseconds

from mpi4py import MPI
comm = MPI.COMM_WORLD

# setup and simulate

nest.ResetKernel()

nest.SetKernelStatus({'overwrite_files': True, 'resolution': 1.})

music_proxy = nest.Create('music_event_in_proxy', 1, {'port_name': 'in'})

neuron = nest.Create('iaf_psc_delta', 1, {'E_L': -62., 'V_th': -60.})
dummy_neuron = nest.Create('iaf_psc_delta', 1, {'E_L': -62., 'V_th': 0.})  # used to record free membrane potential

m = nest.Create('multimeter', 1, {'record_from': ['V_m']})

sd = nest.Create('spike_detector')

nest.Connect(music_proxy, neuron, syn_spec={'weight': 2.})
nest.Connect(music_proxy, dummy_neuron, syn_spec={'weight': 2.})

nest.Connect(m, dummy_neuron)

nest.Connect(neuron, sd)

comm.Barrier()  # necessary to synchronize with MUSIC

nest.Simulate(simtime)

# plot results

vm = nest.GetStatus(m, 'events')[0]

spikes = nest.GetStatus(sd, 'events')[0]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Membrane potential (mV)')
ax.set_xlim([0., simtime])
ax.set_ylim([-65., -45.])

ax.plot(spikes['times'], [-50.] * len(spikes['times']), 'ko')
ax.plot(vm['times'], vm['V_m'], 'k')

plt.show()
