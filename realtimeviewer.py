import pygame
import numpy as np
from shipsims import ship
import time
import neuralnetwork as nn
import particlesystem as ps
import particle as p
import nnvis
import ctypes
class RealtimeViewer():
    def __init__(self, genome, layer_sizes, sim_class, PHYS_STEP):
        self.genome = genome
        self.net = nn.NeuralNetwork(layer_sizes)
        self.PHYS_STEP = PHYS_STEP
        weights = self.net.import_genome(genome, layer_sizes)
        pygame.init()
        size = width, height = 1920, 1080
        ctypes.windll.user32.SetProcessDPIAware()
        self.sim_class = sim_class
        self.ship = sim_class(width/2, height/2, width, height,  do_draw = True, max_time = 60)

        self.screen = pygame.display.set_mode(size)
        self.now = 0
        self.gameExit = False

        self.nnvis = nnvis.NNVis(weights, layer_sizes, [1920 - 500, 1080 - 500], 400, 400)

    def start(self):
        dtSim = 0
        self.now = time.time()
        #time.sleep(5)
        inputs = self.ship.get_inputs()
        while not self.gameExit:
            dt = (time.time() - self.now)
            dtSim += dt

            # Only aadjust contols as they were adjusted in simulation
            if dtSim >= self.PHYS_STEP:
                inputs = self.ship.get_inputs()
                outputs = self.net.predict(inputs)
                self.ship.set_controls(controls = outputs)
                dtSim = 0
                self.ship.update(self.PHYS_STEP)

            self.now = time.time()

            # Drawing
            self.ship.update_parts(dt)
            self.screen.fill((0,0,0))
            self.ship.draw(self.screen)
            self.nnvis.draw(inputs, self.screen)
            pygame.display.flip()

            if self.ship.status()[0] == 0:
                self.reset()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
            #time.sleep(1.0/120.0)
    def reset(self):
        del self.ship
        width, height = 1920, 1080
        self.ship = self.sim_class(width/2, height/2, width, height, do_draw = True, max_time = 60)
        self.now = time.time()
