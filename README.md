# simulated-craft-neuralnet
Controlling simulated spacecraft with genetic algorithm &amp; neural network

This project was created in collaboration with Louis Lebouef.

If you wish to run this project, you will need:
- pygame

NOTE: This is still a work in progress.
The user-friendly interface is not complete. Run generator.py and edit parameters within to get an idea of how this project works (sorry).

# What is this project?
This project provides:
- Multiple simlulated craft, each with their own unique control schemes (two bidirectional thrusters, single gimbaled thrust, dual gimbaled thrusters, etc.)
- Neural network and genetic algorithm training modules
- Ability to train the neural networks to fly these craft to their 'goal destinations'
- A realtime visualization module to view both the craft and the activity of the neural network

# Example
Here's the results after 500 generations of evolution:

https://user-images.githubusercontent.com/69018340/120042115-18caa000-bfcf-11eb-86e0-71c8069b70dd.mp4

As you can see, there is still some room for improvement, especially with this complex dual-thruster configuration.

This project was inspired by John Buffer's AutoDrone project, available [here](https://github.com/johnBuffer/AutoDrone)

Other resources used:

[Sebastian Lague: Neural Networks series](https://www.youtube.com/watch?v=bVQUSndDllU)

[Kie Codes: Genetic Algorithm in Python](https://www.youtube.com/watch?v=nhT56blfRpE)
