#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import numpy as np

from mpi4py import MPI
comm = MPI.COMM_WORLD

simtime = 5000.
tau_m = 1.
tau_syn = 50.

# setup and simulate

nest.ResetKernel()

nest.SetKernelStatus({'overwrite_files': True, 'resolution': 1.})

music_in_proxy = nest.Create('music_event_in_proxy', 1, {'port_name': 'in'})

neuron_left = nest.Create('iaf_psc_exp', 1, {'E_L': -59.5, 'V_th': -60., 'tau_m': tau_m, 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn})
neuron_right = nest.Create('iaf_psc_exp', 1, {'E_L': -60.5, 'V_th': -60., 'tau_m': tau_m, 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn})

sd = nest.Create('spike_detector')

sd_ev = nest.Create('spike_detector')

mv_left = nest.Create('multimeter', 1, {'record_from': ['V_m']})
mv_right = nest.Create('multimeter', 1, {'record_from': ['V_m']})

nest.Connect(music_in_proxy, neuron_left, syn_spec={'weight': -200.})
nest.Connect(music_in_proxy, neuron_right, syn_spec={'weight': 200.})

nest.Connect(neuron_left, sd)
nest.Connect(neuron_right, sd)

nest.Connect(mv_left, neuron_left)
nest.Connect(mv_right, neuron_right)

nest.Connect(music_in_proxy, sd_ev)

comm.Barrier()  # necessary to synchronize with MUSIC

nest.Simulate(simtime)

# plot results

print('event rate', nest.GetStatus(sd_ev, 'n_events')[0] / simtime * 1e3)

spikes = nest.GetStatus(sd, 'events')[0]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel('Time (ms)')
ax.set_xlim([0., simtime])
ax.set_ylim([neuron_left[0] - 1, neuron_right[0] + 1])
ax.set_yticks([neuron_left[0], neuron_right[0]])
ax.set_yticklabels(['Left', 'Right'])

ax.plot(spikes['times'], spikes['senders'], 'bo', label='Spikes', markeredgewidth=0, markersize=2)

fig.savefig('nest_output.png', dpi=300)
