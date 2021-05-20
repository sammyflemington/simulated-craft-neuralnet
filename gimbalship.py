import numpy as np
import pygame
import math
import particlesystem as ps
import particle as p
class SpinShip():
    def __init__(self, x, y, width, height, goal_thresh = 10, max_time = 60):
        self.screen_width = width
        self.screen_height = height
        self.partsys = ps.ParticleSystem()
        self.angle = -math.pi/2
        self.goal_positions =  [[3*width/4, height/4],[width/4, height/4],[width/2, height/2],[2*width/3, 1*height/3]]##
        #self.goal_positions = (np.random.rand(10,2)*700 + (150*np.ones((10, 2))) + [[np.random.randint(0, high = 800), 0]])
        self.time_in = 0
        self.time_out = 0
        self.goal_counter = 0
        self.GOAL_THRESH = goal_thresh
        self.timer = 0.0
        self.max_time = max_time
        self.closest_to_goal = 99999999
        self.max_speed = 5
        self.x = x
        self.y = y
        self.velocity = [0.0,0.0]
        self.MAXTHRUST : float= 3000.0
        self.ANGTHRUST : float= 5.0
        self.angular_velocity : float = 0.0
        self.GRAVITY = 750.0
        self.image = pygame.image.load("lander.png")
        self.goalimg = pygame.image.load("lander.png")
        self.scale = 0.3
        self.thrust : float = 0.0
        self.angular_thrust : float = 0.0
        self.goal_time = 3
        self.active = 1
        self.touching_goal = False

    def end_trial(self, code):
        self.active = 0
        #print(code)
        if code == "CRASH":
            self.goal_counter = 0
            self.time_out = self.max_time
            self.closest_to_goal = 10000

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
        # Apply Controls & gravity
        self.thrust = max(-self.MAXTHRUST, min(self.thrust, self.MAXTHRUST))
        #self.angular_thrust = max(-self.ANGTHRUST, min(self.angular_thrust, self.ANGTHRUST))
        #print("TEST:",self.velocity, self.angle, self.MAXTHRUST, self.thrust,"OVER")
        self.angle += self.ANGTHRUST * self.angular_thrust * dt
        self.angle = max(-(math.pi/6) - math.pi/2, min(self.angle, (math.pi/6)- math.pi/2))
        #print("TEST:",self.velocity, self.angle, self.MAXTHRUST, self.thrust, "OVER")
        self.velocity[0] += math.cos(self.angle) * self.MAXTHRUST * dt * self.thrust
        self.velocity[1] += math.sin(self.angle) * self.MAXTHRUST * dt * self.thrust

        # gravity
        self.velocity[1] += self.GRAVITY * dt

        np.clip(self.velocity, a_min = -self.max_speed, a_max = self.max_speed)
        # position
        self.x = np.add(self.x, self.velocity[0] * dt)
        self.y = np.add(self.y, self.velocity[1] * dt)

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
        thrustx = -800 * self.thrust * math.cos(self.angle)
        thrusty = -800 * self.thrust * math.sin(self.angle)
        thrust = (thrustx**2 + thrusty**2)**.5
        self.partsys.create_particle(
            p.Particle(self.x, self.y,
            thrustx + self.velocity[0], thrusty + self.velocity[1], thrust/8,
            .9, .5, (max( min(255*thrust, 255), 0), 50, 50)))
        self.partsys.update(dt)
    def draw(self, display):
        # Draw Self
        self.partsys.draw(display)
        l = len(self.goal_positions)
        img = pygame.transform.rotozoom(self.image, -(self.angle*180/math.pi)-90, self.scale)
        rect = img.get_rect()
        rect.center = (self.x,self.y)
        display.blit(img, rect)

        # Draw Goals
        # gi = self.goalimg
        # gi = pygame.transform.rotozoom(gi, 0, .1)
        # display.blit(gi, (self.goal_positions[self.goal_counter%l][0],self.goal_positions[self.goal_counter%l][1]))
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
                self.y - self.goal_positions[self.goal_counter%l][1], self.velocity[0], self.velocity[1], self.angle,
                self.angular_velocity]

    def set_controls(self, thrust : float, ang_t : float):
        self.thrust = max(0, min((thrust*2) - 1, 1))
        self.angular_thrust = max(-1, min((ang_t*2) - 1, 1))
