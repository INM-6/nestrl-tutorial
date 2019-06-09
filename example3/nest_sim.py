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


simtime = 5000.  # needs to match the stoptime (here in ms) defined in the music config
max_rate = 50.  # needs to match the max rate defined for the encoder in the music config
J = 250.

# setup and simulate

nest.ResetKernel()

tau_m = nest.GetDefaults('iaf_psc_exp', 'tau_m')
tau_syn_ex = nest.GetDefaults('iaf_psc_exp', 'tau_syn_ex')
tau_syn_in = nest.GetDefaults('iaf_psc_exp', 'tau_syn_in')
assert abs(tau_syn_ex - tau_syn_in) < 1e-9
C_m = nest.GetDefaults('iaf_psc_exp', 'C_m')

music_event_in = nest.Create('music_event_in_proxy', 1, {'port_name': 'in'})

neuron_left = nest.Create('iaf_psc_exp', 1, {
    # since the default action is "accelerate right" the car will spend most
    # time in the left half; we reduced the resting potential of the
    # left-coding neurons to make it a bit less excitable and make the
    # difference between the two neurons more visible
    'E_L': -60.4 + get_current_offset(J, max_rate / 2., tau_m, tau_syn_ex, C_m),
    'V_th': -60.
})
neuron_right = nest.Create('iaf_psc_exp', 1, {
    'E_L': -60. + get_current_offset(-J, max_rate / 2., tau_m, tau_syn_ex, C_m),
    'V_th': -60.
})

sd = nest.Create('spike_detector')

nest.Connect(music_event_in, neuron_left, syn_spec={'weight': -J})
nest.Connect(music_event_in, neuron_right, syn_spec={'weight': J})

nest.Connect(neuron_left, sd)
nest.Connect(neuron_right, sd)

comm.Barrier()  # necessary to synchronize with MUSIC

nest.Simulate(simtime)

# plot results

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
