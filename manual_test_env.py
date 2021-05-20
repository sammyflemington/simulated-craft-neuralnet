import pygame
import numpy as np
import sys
from shipsims import drone
import time
import math

pygame.init()
size = width, height = 1280, 720

ship = drone.Drone(width/2, height/2, width, height, do_draw = True)

speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)
now = time.time()
thrust = 0
ang_thrust = 0
rot = 0
while 1:

    pressed = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        mp = pygame.mouse.get_pos()
        dir = math.atan2(mp[0] - ship.x,(mp[1] - ship.y)) / math.pi
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                rot = -1
            elif event.key == pygame.K_DOWN:
                rot = 1
            else:
                thrust = 0
            if event.key == pygame.K_RIGHT:
                thrust = -1
            elif event.key == pygame.K_r:
                del ship
                ship = drone.Drone(width/2, height/2, width, height, do_draw = True)
            elif event.key == pygame.K_LEFT:
                ang_thrust = -1
            else:
                ang_thrust = 0
        elif event.type == pygame.KEYUP:
            thrust = 0
            ang_thrust = 0
    dt = (time.time() - now)

    print("Thrust:",thrust,"Ang Thrust:",ang_thrust)
    #print(round(ship.x),round(ship.y))
    print("ANG: ",ship.angle)
    if dt > 1/120:
        now = time.time()
        screen.fill(black)
        ship.update(dt)
        ship.update_parts(dt)
        ship.set_controls(controls = [thrust, ang_thrust])#, rot, rot])
        ship.draw(screen)


        pygame.display.flip()
