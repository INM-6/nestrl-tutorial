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

before you start, please make sure to have all paths set correctly (see add_paths.sh)

Example 0: Python to Python via ZeroMQ
---------------------------------------

we start with a simple setup in which we send data from one python script to another via zmq sockets
if you are already familiar with zmq, you can skip this step

we want to communicate asynchronously and use a publisher/subscriber mode, also used throughout gymz 
these messages have a particular from, which also gymz uses to communicate observations from environments (see example0/zmq_sender.py)
they consist of a list of dictionaries in json format, one dictionary for each observation channel, with each dictionary containing an observed value, the limits of this value and a timestamp
the limits are necessary to normalize the data in the subsequent MUSIC adapters and the timestamp is used to detect desynchronization between different parts of the toolchain
although we would not need this specific message type in this example, it is useful to use the same format also used later

we set up a publisher (zmq.PUB) that continously sends out messages (see <https://pyzmq.readthedocs.io/en/latest/index.html> for all zmq specific details)
the sender.py script just sends a sine wave for t_max seconds with a time step between two messages of dt
the receiver registers as a subscriber (zmq.SUBSCRIBE) to the zmq publisher and print the received messages to the screen

to run this example, start the sender and the subscriber, and watch the subscriber print messages to the screen

.. code:: bash

          $ ./zmq_sender.py&
          $ ./zmq_receiver.py


Example 1: Python to Python via ZeroMQ & MUSIC
-----------------------------------------------

we now include MUSIC in the loop; although this setup is quite artificial  it illustrates some feature of the zmq adapters

we will use the zmq scripts from the previous example, but note that now, we need to set a different port in the receiver, otherwise it just directly receives data from sender.py
for this we will use a zmq_cont_adapter which translates data from zero mq, in the message format defined above, to continuous values that can be understood by MUSIC
we will then use a threshold adapter to remove all values smaller than zero and will sends its output to a cont_zmq_adapter that transforms continuous data from MUSIC back to our message format

we need to define our setup in a MUSIC config file [link to MUSIC doc?] (see example1/config.music)
first of all we need an adapter that connects to a zmq publisher, receives messages and converts them into a continious variable, the zmq_cont_adapter (read ZeroMQ->Continuous value adapter)
we need to define the MUSIC time step, for which we choose the same value as in the sender
we also set the message type to expect to GymObservation, which has the same format as we defined in sender
finally, we tell the adapter to connect to the sender running on localhost on the corresponding port
as a second adapter, we use the threshold adapter, in which we disable the heaviside, i.e., step function behaviour and turn it into a threshold-linear adapter by setting heaviside to false and threshold to zero
the converting the data from the threshold adapter back to zmq messages happens via a cont_zmq_adapter ("Continous value->ZeroMQ adapter")
we need to additionally provide the min and max of the values, that we expect and define on which port to publish the messages
at last, we hook up the various binaries, and define which MUSIC ports to connect

you can then run the example by starting the sender and receiver, and then running MUSIC with an appropiate number of processes
you should see a similar output as in the first example, but now all negative values are set to zero due to the threshold-linear adapter

.. code:: bash

          $ ./zmq_sender.py&
          $ ./zmq_receiver.py&
          $ mpirun -np 3 music config.music


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
          $ mpirun -np 3 music config.music


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
