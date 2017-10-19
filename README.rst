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

[IDEA: build everything up from scratch, only introduce one new script at a time]

Example 0: Python to Python via ZeroMQ
---------------------------------------

we start with a simple setup in which we send data from one python script to another via zmq sockets
if you are already familiar with zmq, you can skip this step

we want to communicate asynchronously and use a publisher/subscriber mode, also used throughout gymz
these messages have a particular from, which also gymz uses to communicate observations from environments
they consist of a list of dictionaries in json format, one dictionary for each observation channel, with each dictionary containing an observed value, the limits of this value and a timestamp
the limits are necessary to normalize the data in the subsequent MUSIC adapters and the timestamp is used to detect desynchronization between different parts of the toolchain
although we would not need this specific message type in this example, it is useful to use the same format also used later

we set up a publisher (zmq.PUB) that continously sends out messages (see <https://pyzmq.readthedocs.io/en/latest/index.html> for all zmq specific details)
the sender.py script just sends a sine wave for t_max seconds with a time step between two messages of dt
the receiver registers as a subscriber (zmq.SUBSCRIBE) to the zmq publisher and print the received messages to the screen

to run this example, start the sender and the subscriber, and watch the subscriber print messages to the screen

.. code:: bash

          $ ./zmq_sender.py
          $ mpirun -np 3 music music_setup.music

Example 1: Python to Python via ZeroMQ & MUSIC
-----------------------------------------------

Example 2: Python to NEST via ZeroMQ & MUSIC
-------------------------------------------

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

Example 3: OpenAI Gym to NEST via ZeroMQ & MUSIC
------------------------------------------------

now create a simple setup in which we use the toolchain to feed observations from an environment from OpenAI Gym into a simulation with two neurons that mimic place cells
we use the MountainCar environment and the neurons respond to to the agent being in the left half, and the right half of the screen, respectively

Example 4: OpenAI Gym to NEST and back via ZeroMQ & MUSIC
---------------------------------------------------------

TODO (what I realized is missing during writing this)
=====================================================
- explain every entry in default config
- documentation for all adapters/encoders
- explain message types
- MUSIC is not very user friendly in terms of error messages, we should help to improve this
