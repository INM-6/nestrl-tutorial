#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import numpy as np

from mpi4py import MPI
comm = MPI.COMM_WORLD

simtime = 10000.

# setup and simulate

nest.ResetKernel()

nest.SetKernelStatus({'overwrite_files': True, 'resolution': 1.})

music_in_proxy = nest.Create('music_event_in_proxy', 1, {'port_name': 'in'})
music_out_proxy = nest.Create('music_event_out_proxy', 1, {'port_name': 'out'})

tau_syn = 50.
neuron_left = nest.Create('iaf_psc_exp', 1, {'E_L': -59.5, 'V_th': -60., 'tau_m': 1., 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn})
neuron_right = nest.Create('iaf_psc_exp', 1, {'E_L': -60.5, 'V_th': -60., 'tau_m': 1., 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn})

neuron_command = nest.Create('iaf_psc_exp', 1, {'E_L': -60., 'V_th': -60., 'tau_m': 1., 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn})

sd = nest.Create('spike_detector')

sd_ev = nest.Create('spike_detector')

mv_left = nest.Create('multimeter', 1, {'record_from': ['V_m']})
mv_right = nest.Create('multimeter', 1, {'record_from': ['V_m']})
mv_command = nest.Create('multimeter', 1, {'record_from': ['V_m']})

nest.Connect(music_in_proxy, neuron_left, syn_spec={'weight': -200.})
nest.Connect(music_in_proxy, neuron_right, syn_spec={'weight': 200.})

nest.Connect(neuron_left, neuron_command, syn_spec={'weight': 200.})
nest.Connect(neuron_right, neuron_command, syn_spec={'weight': -200.})

nest.Connect(neuron_command, music_out_proxy, syn_spec={'receptor_type': 0})

nest.Connect(neuron_left, sd)
nest.Connect(neuron_right, sd)
nest.Connect(neuron_command, sd)

nest.Connect(mv_left, neuron_left)
nest.Connect(mv_right, neuron_right)
nest.Connect(mv_command, neuron_command)

nest.Connect(music_in_proxy, sd_ev)

comm.Barrier()  # necessary to synchronize with MUSIC

nest.Simulate(simtime)

# plot results

print('events', nest.GetStatus(sd_ev, 'n_events')[0] / simtime * 1e3)

spikes = nest.GetStatus(sd, 'events')[0]

fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_xlabel('Time (ms)')
ax.set_xlim([0., simtime])
ax.set_ylim([neuron_left[0] - 1, neuron_command[0] + 1])
ax.set_yticks([neuron_left[0], neuron_right[0], neuron_command[0]])
ax.set_yticklabels(['Left', 'Right', 'Command'])

ax.plot(spikes['times'], spikes['senders'], 'ko')

ax2 = fig.add_subplot(212)

vm_left = nest.GetStatus(mv_left, 'events')[0]
vm_right = nest.GetStatus(mv_right, 'events')[0]
vm_command = nest.GetStatus(mv_command, 'events')[0]

ax2.plot(vm_left['times'], vm_left['V_m'], 'r', label='left')
ax2.axhline(np.mean(vm_left['V_m'][100:]), lw=2, color='r')
ax2.plot(vm_right['times'], vm_right['V_m'], 'b', label='right')
ax2.axhline(np.mean(vm_right['V_m'][100:]), lw=2, color='b')
ax2.plot(vm_command['times'], vm_command['V_m'], 'm', label='command')

plt.legend()

plt.show()
