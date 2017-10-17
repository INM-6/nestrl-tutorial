Tutorial: Interfacing NEST and OpenAI Gym
=========================================

Preparations
------------

You first need to install a variety of tools:

1. Download and install MUSIC from <https://github.com/incf-music>
2. Download and install MUSIC adapters from <https://github.com/incf-music/music-adapters>
3. Download and install NEST from <https://github.com/nest/nest-simulator>
   Do not forget to set `-Dwith-music=ON`
4. Install OpenAI Gym via pip (<https://pypi.python.org/pypi/gym>)
5. Install gymz via pip (<https://pypi.python.org/pypi/gymz>)


Example 0: Input via ZeroMQ
---------------------------

as first step, we feed custom input from a Python script via ZeroMQ into a neuron in NEST

we start with a simple Python script that sends a sine wave via a ZeroMQ socket (see zmq_sender.py)
note that the message needs to have a certain format (see [link to adapter doc])

this data needs to be received by a MUSIC adapter and converted into spikes before it can be used in NEST
for this we use the zmq_cont_adapter that receives data in the format specified above and scales the value to the range [-1, 1] (see music_setup.music)
to convert this continuos value into spikes, we connect the output of the zmq_cont_adapter to an encoder
this receives continous data and produces regular spike trains. to determine the rate of the spiketrain, one can define a minimal and a maximal rate
the value received (expected to be between [-1, 1]) is then converted to an appropiate rate
this spiketrain can now be fed into a neuron in NEST

in nest, we create a music proxy, that receives spikes (music_event_in_proxy), since it should receive data, we need to specify the port name "in"
we then can directly connect this proxy to a neuron; in our setup we use two neurons to record the spiketrain and the free membrane potential at the same time

to run this example, you first start zmq_sender.py and then launch music with mpirun and the appropiate number of processes:

.. code:: bash

          $ ./zmq_sender.py
          $ mpirun -np 3 music music_setup.music

make sure to have all paths set correctly (see add_paths.sh)

Example 1: Input from OpenAI Gym
--------------------------------

now create a simple setup in which we use the toolchain to feed observations from an environment into a simulation with two neurons
we use the MountainCar environment and two neurons that respond to the agent being in the left half, or the right half of the screen

TODO (what I realized is missing during writing this)
=====================================================
- explain every entry in default config
- documentation for all adapters/encoders
- explain message types
