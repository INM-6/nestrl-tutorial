todo:
- explain every entry in default config

Tutorial: Interfacing NEST and OpenAI Gym
=========================================

You first need to install a variety of tools:

1. Download and install MUSIC from <https://github.com/incf-music>
2. Download and install MUSIC adapters from <https://github.com/incf-music/music-adapters>
3. Download and install NEST from <https://github.com/nest/nest-simulator>
   Do not forget to set `-Dwith-music=ON`
4. Install OpenAI Gym via pip (<https://pypi.python.org/pypi/gym>)
5. Install gymz via pip (<https://pypi.python.org/pypi/gymz>)

now create a simple setup in which we use the toolchain to feed observations from an environment into a simulation with two neurons
we use the MountainCar environment and two neurons that respond to the agent being in the left half, or the right half of the screen


