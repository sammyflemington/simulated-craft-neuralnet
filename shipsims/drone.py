import numpy as np
import particlesystem as ps
import particle as p
import pygame
import math

class Drone():
    max_speed = 5
    GRAVITY = 750.0
    scale = .5
    arm_length = 40
    MAXTHRUST = 2000.0
    MOI = 3
    def __init__(self, x, y, width, height, goal_thresh = 30, max_time = 15, do_draw = False):
        self.screen_width = width
        self.screen_height = height

        self.do_draw = do_draw
        self.goal_positions =  [[width/2  + 50, height/4],[1*width/4, height/4],[width/4, height/4],[2*width/3, 1*height/3]]##
        #self.goal_positions = (np.random.rand(10,2)*700 + (150*np.ones((10, 2))) + [[np.random.randint(0, high = 800), 0]])
        self.time_in = 0
        self.time_out = 0
        self.goal_counter = 0
        self.GOAL_THRESH = goal_thresh
        self.timer = 0.0
        self.max_time = max_time
        self.closest_to_goal = 99999999
        self.x = x
        self.y = y
        self.velocity = [0.0,0.0]

        self.goal_time = 3
        self.active = 1
        self.touching_goal = False
        if (self.do_draw):
            self.image = pygame.image.load("assets/drone.png")
            self.goalimg = pygame.image.load("assets/lander.png")
            self.partsys = ps.ParticleSystem()

        self.lthrust : float = 0.0
        self.rthrust : float = 0.0

        self.angle = -math.pi/2
        self.ang_vel : float = 0.0

    def end_trial(self, code):
        self.active = 0
        #print(code)
        if code == "CRASH":
            #self.goal_counter = 0
            self.time_out = self.max_time
            #print(self.time_in)
            #self.closest_to_goal = 1000

    def check_for_goal(self, dt):
        l = len(self.goal_positions)
        goalX = self.goal_positions[self.goal_counter%l][0]
        goalY = self.goal_positions[self.goal_counter%l][1]
        dist = math.sqrt(((self.x - goalX)**2) + ((self.y - goalY)**2))
        if (dist < self.closest_to_goal):
            self.closest_to_goal = dist

        if (abs(self.x - self.goal_positions[self.goal_counter%l][0]) < self.GOAL_THRESH and
            abs(self.y - self.goal_positions[self.goal_counter%l][1]) < self.GOAL_THRESH):
            # Gain time in
            self.touching_goal = True
            self.time_in += dt
            # IF on this goal for self.goal_time sec, new goal
            if (self.time_in >= (self.goal_counter + 1) * self.goal_time):
                self.goal_counter += 1
                self.closest_to_goal = 10000
        else:
            # Gain time out
            self.time_out += dt
            self.touching_goal = False

    def update(self, dt : float):
        # angular acceleration
        if self.active:
            MR = (self.rthrust * Drone.arm_length)
            ML = -(self.lthrust * Drone.arm_length)

            self.ang_vel += ((MR + ML) * dt)/Drone.MOI
            self.angle += self.ang_vel * dt

            # Apply forces
            totalThrust = (self.rthrust + self.lthrust) * Drone.MAXTHRUST
            self.velocity[0] += totalThrust * math.cos(self.angle) * dt
            self.velocity[1] += totalThrust * math.sin(self.angle) * dt
            # print("THRUST: R: ",self.rthrust, " L: ", self.lthrust)
            # print("VEL: X: ", self.velocity[0], " Y: ", self.velocity[1])
            # Gravity
            self.velocity[1] += Drone.GRAVITY * dt
            # Apply velocity chang
            self.x += self.velocity[0] * dt
            self.y += self.velocity[1] * dt

            # Check for out of bounds (CRASH)
            if (self.x < 0 or self.x > self.screen_width or
                self.y < 0 or self.y > self.screen_height):
                self.end_trial("CRASH")

            self.timer += dt

            # Check for timeout
            if (self.timer >= self.max_time):
                self.end_trial("TIMEOUT")

            self.check_for_goal(dt)

    def update_parts(self, dt):
        rthrust = -800 * self.rthrust
        lthrust = -800 * self.lthrust
        xscl = math.cos(self.angle + math.pi/2)
        yscl = math.sin(self.angle + math.pi/2)
        xsclv = math.cos(self.angle )
        ysclv = math.sin(self.angle )
        if self.do_draw:
            #Right
            self.partsys.create_particle(
                p.Particle(self.x - (Drone.arm_length * xscl), self.y - (Drone.arm_length * yscl),
                (rthrust * xsclv) + self.velocity[0], (rthrust*ysclv) + self.velocity[1], abs(rthrust)/ 20,
                .95, 1, (max( min(255*abs(rthrust), 255), 0), 0, 255)))

            #left
            self.partsys.create_particle(
                p.Particle(self.x + (Drone.arm_length * xscl), self.y + (Drone.arm_length * yscl),
                (lthrust * xsclv) + self.velocity[0], (lthrust*ysclv) + self.velocity[1], abs(lthrust)/ 20,
                .95, 1, (max( min(255*abs(lthrust), 255), 0), 255, 0)))

            self.partsys.update(dt)
    def draw(self, display):
        # Draw Self
        if self.do_draw:

            l = len(self.goal_positions)
            img = pygame.transform.rotozoom(self.image, -(self.angle*180/math.pi)-90, Drone.scale)
            rect = img.get_rect()
            rect.center = (self.x,self.y)
            display.blit(img, rect)
            self.partsys.draw(display)
            #print("THRUST: R: ",self.rthrust, " L: ", self.lthrust)
            # Draw Goals
            # print("INPUTS: GX:", self.x - self.goal_positions[self.goal_counter%l][0],"\nGY:",
            #     self.y - self.goal_positions[self.goal_counter%l][1], "\nANG:",self.angle,"\nANG_V:",self.ang_vel)
            if self.touching_goal:
                color = (0, 255, 0)
            else:
                color = (255, 0, 0)
            pygame.draw.circle(display, color, (self.goal_positions[self.goal_counter%l][0],self.goal_positions[self.goal_counter%l][1]), 10)

    def status(self):
        return [self.active, self.time_in, self.time_out, self.goal_counter, self.closest_to_goal]

    def get_inputs(self):
        l = len(self.goal_positions)
        return [self.x - self.goal_positions[self.goal_counter%l][0],
                self.y - self.goal_positions[self.goal_counter%l][1], self.velocity[0], self.velocity[1], self.angle]
        # return [self.x - self.goal_positions[self.goal_counter%l][0],
        #         self.y - self.goal_positions[self.goal_counter%l][1], self.velocity[0], self.velocity[1], self.angle,
        #         self.ang_vel]

    def set_controls(self, controls = [0,0]):
        self.lthrust = max(-1, min(controls[0], 1))
        self.rthrust = max(-1, min(controls[1], 1))
