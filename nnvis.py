import numpy as np
import pygame
import math
import neuralnetwork as nn

class NNVis():


    def __init__(self, weights, layer_sizes, location, width, height):
        self.weights = weights
        self.layer_sizes = layer_sizes
        self.location = location
        self.width = width
        self.height = height
        self.wmargin = 50
        self.hmargin = 50
        self.nsize = 10
        self.ssize = 5
        self.positions = []
        self.surf = pygame.Surface((width+(self.wmargin*2), height+(self.hmargin*2)))
    def draw(self, inputs, display):
        self.positions = []
        hspace = self.width / len(self.weights)
        vspace = self.height / len(self.weights[0][0])
        for i in range(self.layer_sizes[0]):
            self.positions.append([self.wmargin, (vspace * i) + (vspace / 2) + self.hmargin])
        # For each VECTOR in loop, draw NEURONS
        loop = 1

        # Draw input neurons

        for i in range(len(inputs)):
            color = self.make_color(inputs[i])
            pygame.draw.circle(self.surf, color, (self.positions[i][0], self.positions[i][1]), 10)

        for w in self.weights:
            # Find vector product of input and each weight to find line values
            # self.positions holds positions of previous layer's neurons
            # Positions of neurons to the right
            new_positions = []
            hspace = self.width / len(self.weights)
            vspace = self.height / len(w)
            for i in range(len(w)):# Number of neurons in next column of them
                new_positions.append([hspace * loop + self.wmargin, (vspace * i) + (vspace / 2) + self.hmargin])


            r = 0
            for row in w: # ROW is LEFT
                neuron_val = 0
                for entry in range(len(row)):# ENTRY is RIGHT
                    synapse_val = row[entry] * inputs[entry]
                    # This line connects neuron "entry" on the left to
                    # neuron "row" on the right.

                    # Add up each line value to get the neuron value (dot product)
                    neuron_val += synapse_val
                    # Draw line connecting neurons (synapses)
                    color = self.make_color(synapse_val)
                    pygame.draw.line(self.surf, color,
                        (self.positions[entry][0], self.positions[entry][1]),
                        (new_positions[r][0], new_positions[r][1]), width = abs(round(self.ssize * row[entry]))+ 2)
                # Draw neuron
                color = self.make_color(neuron_val)
                pygame.draw.circle(self.surf, color, (new_positions[r][0],new_positions[r][1]), self.nsize)
                r += 1

            inputs = self.activation(np.matmul(w,inputs))
            self.positions = new_positions
            loop += 1

        display.blit(self.surf, (self.location[0], self.location[1]))

    @staticmethod
    def activation(x):
        #return np.tanh(x)
        return (1/(1+np.exp(-np.clip(x, a_min = -4, a_max = 4))))

    def make_color(self, value):
        x = self.activation(value) - 0.5
        col = (min( abs(255* min(x, 0)), 255),  # negative part red
                min(255* max(x, 0), 255),        # Positive part green
                100)
        #print(col)
        return col
