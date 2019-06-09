#!/usr/bin/env python

import matplotlib.pyplot as plt
import nest
import numpy as np

from mpi4py import MPI
comm = MPI.COMM_WORLD


def get_current_offset(weight, rate, tau_m, tau_syn, C_m):
    """
    Computes the mean input expected from an input with rate `rate`
    and weight `weight` for a neuron with parameters `tau_m`,
    `tau_syn` and `C_m` (see Campbell's theorem).

    """
    return weight / C_m * rate * tau_m * tau_syn * 1e-3


simtime = 10000.  # needs to match the stoptime (here in ms) defined in the music config
max_rate = 50.  # needs to match the max rate defined for the encoder in the music config

tau_m = 1.
tau_syn = 20.
J = 200.

# setup and simulate

nest.ResetKernel()

nest.SetKernelStatus({'resolution': 1.})

C_m = nest.GetDefaults('iaf_psc_exp', 'C_m')

music_in_proxy = nest.Create('music_event_in_proxy', 1, {'port_name': 'in'})
music_out_proxy = nest.Create('music_event_out_proxy', 1, {'port_name': 'out'})

neuron_left = nest.Create('iaf_psc_exp', 1, {
    'E_L': -60.3 + get_current_offset(J, max_rate / 2., tau_m, tau_syn, C_m),  # add additional 0.3mV to make the left neuron a bit less excitable
    'V_th': -60., 'tau_m': tau_m, 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn, 'C_m': C_m
})
neuron_right = nest.Create('iaf_psc_exp', 1, {
    'E_L': -60. + get_current_offset(-J, max_rate / 2., tau_m, tau_syn, C_m),
    'V_th': -60., 'tau_m': tau_m, 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn, 'C_m': C_m
})

neuron_command = nest.Create('iaf_psc_exp', 1, {'E_L': -60., 'V_th': -60., 'tau_m': 10 * tau_m, 'tau_syn_ex': tau_syn, 'tau_syn_in': tau_syn})

sd = nest.Create('spike_detector')

mv_left = nest.Create('multimeter', 1, {'record_from': ['V_m']})
mv_right = nest.Create('multimeter', 1, {'record_from': ['V_m']})
mv_command = nest.Create('multimeter', 1, {'record_from': ['V_m']})

nest.Connect(music_in_proxy, neuron_left, syn_spec={'weight': -J})
nest.Connect(music_in_proxy, neuron_right, syn_spec={'weight': J})

nest.Connect(neuron_left, neuron_command, syn_spec={'weight': J})
nest.Connect(neuron_right, neuron_command, syn_spec={'weight': -J})

nest.Connect(neuron_command, music_out_proxy)

nest.Connect(neuron_left, sd)
nest.Connect(neuron_right, sd)
nest.Connect(neuron_command, sd)

nest.Connect(mv_left, neuron_left)
nest.Connect(mv_right, neuron_right)
nest.Connect(mv_command, neuron_command)

comm.Barrier()  # necessary to synchronize with MUSIC
nest.Simulate(simtime)

# plot results

spikes = nest.GetStatus(sd, 'events')[0]

fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_xlim([0., simtime])
ax.set_ylim([neuron_left[0] - 1, neuron_command[0] + 1])
ax.set_yticks([neuron_left[0], neuron_right[0], neuron_command[0]])
ax.set_yticklabels(['Left', 'Right', 'Command'])

ax.plot(spikes['times'], spikes['senders'], 'ko')

ax2 = fig.add_subplot(212)
ax2.set_xlabel('Time (ms)')
ax2.set_ylabel('Membrane potential (mV)')

vm_left = nest.GetStatus(mv_left, 'events')[0]
vm_right = nest.GetStatus(mv_right, 'events')[0]
vm_command = nest.GetStatus(mv_command, 'events')[0]

ax2.plot(vm_left['times'], vm_left['V_m'], 'r', label='left')
ax2.axhline(np.mean(vm_left['V_m'][100:]), lw=2, color='r')
ax2.plot(vm_right['times'], vm_right['V_m'], 'b', label='right')
ax2.axhline(np.mean(vm_right['V_m'][100:]), lw=2, color='b')
ax2.plot(vm_command['times'], vm_command['V_m'], 'm', label='command')

plt.legend()

fig.savefig('nest_output.png', dpi=300)
