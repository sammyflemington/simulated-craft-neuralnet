import numpy as np
import particlesystem as ps
import particle as p
import pygame
import math

class GimbalDrone():
    max_speed = 5
    GRAVITY = 750.0
    scale = .5
    arm_length = 40
    MAXTHRUST = 2000.0
    MOI = 3
    ANGTHRUST = 5
    ANGVEL_MAX = 50
    def __init__(self, x, y, width, height, goal_thresh = 30, max_time = 15, do_draw = False):
        self.screen_width = width
        self.screen_height = height
        #self.log = []
        self.do_draw = do_draw
        self.goal_positions =  [[7*width/12, 1*height/3],[width/2  , height/4],[1*width/4, height/2],[width/4, height/4]]##
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
        self.thrusterR = GimbalDrone.Thruster(-GimbalDrone.arm_length, do_draw = self.do_draw)
        self.thrusterL = GimbalDrone.Thruster( GimbalDrone.arm_length, do_draw = self.do_draw)
        self.lthrust : float = 0.0
        self.rthrust : float = 0.0
        self.lthrust_ang : float = 0.0
        self.rthrust_ang : float = 0.0
        self.angle = 0
        self.ang_vel : float = 0.0

    def end_trial(self, code):
        self.active = 0
        #print(code)
        if code == "CRASH":
            #self.goal_counter = 0
            self.time_out = self.max_time
    # def save_log(self, location):
    #     f = open(location, 'w')
    #     for g in self.log:
    #         for i in g:
    #             f.write(str(i))
    #             f.write(",")
    #         f.write('\n')
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
            #d = [math.cos(self.angle) * GimbalDrone.arm_length, math.sin(self.angle * GimbalDrone.arm_length)]
            self.thrusterR.update(dt, self.rthrust_ang, self.angle)
            self.thrusterL.update(dt, self.lthrust_ang, self.angle)
            rang = self.thrusterR.get_angle()
            lang = self.thrusterL.get_angle()

            MR =  self.rthrust * GimbalDrone.arm_length * math.sin((self.angle)- rang) # (self.rthrust * GimbalDrone.arm_length) # =r x f
            ML = -self.lthrust * GimbalDrone.arm_length * math.sin((self.angle) - lang) # np.cross([self.lthrust * math.cos(self.lang),self.lthrust *  math.sin(self.lang)], [-math.cos(self.angle) * GimbalDrone.arm_length, -math.sin(self.angle * GimbalDrone.arm_length)])
            #print("MOMENTS:" ,MR," ",ML)
            #print("ANGLE:",self.angle,"RIGHTANG:",self.rang)
            self.ang_vel += ((MR + ML) * dt) / GimbalDrone.MOI
            self.angle += self.ang_vel * dt
            # Apply forces
            self.velocity[0] += ((self.rthrust * math.cos(rang)) + (self.lthrust * math.cos(lang))) * GimbalDrone.MAXTHRUST * dt
            self.velocity[1] += ((self.rthrust * math.sin(rang)) + (self.lthrust * math.sin(lang))) * GimbalDrone.MAXTHRUST * dt
            # print("THRUST: R: ",self.rthrust, " L: ", self.lthrust)
            # print("VEL: X: ", self.velocity[0], " Y: ", self.velocity[1])
            # Gravity
            self.velocity[1] += GimbalDrone.GRAVITY * dt
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

        if self.do_draw:
            rthrust = -GimbalDrone.MAXTHRUST * self.rthrust
            lthrust = -GimbalDrone.MAXTHRUST * self.lthrust
            rang = self.thrusterR.get_angle()
            lang = self.thrusterL.get_angle()
            d = [math.cos(self.angle) * GimbalDrone.arm_length, math.sin(self.angle) * GimbalDrone.arm_length]
            #Right
            self.partsys.create_particle(p.Particle(
                self.x - d[0],
                self.y - d[1],
                self.velocity[0] + ((rthrust+ 100) * math.cos(rang)),
                self.velocity[1] + ((rthrust+ 100) * math.sin(rang)),
                -rthrust/ 50,
                .95, 1, (max( min(255*abs(rthrust), 255), 0), 0, 100)))

            #left
            self.partsys.create_particle(p.Particle(
                self.x + d[0],
                self.y + d[1],
                self.velocity[0] + ((lthrust+ 100) * math.cos(lang)),
                self.velocity[1] + ((lthrust+ 100) * math.sin(lang)),
                -lthrust/ 50,
                .95, 1, (max( min(255*abs(lthrust), 255), 0), 100, 0)))

            self.partsys.update(dt)
    def draw(self, display):
        # Draw Self
        rang = self.thrusterR.get_angle()
        lang = self.thrusterL.get_angle()
        if self.do_draw:
            #self.log.append((str(self.timer), str(self.angle), str(rang), str(lang), str(self.rthrust), str(self.lthrust)))
            l = len(self.goal_positions)
            img = pygame.transform.rotozoom(self.image, -(self.angle*180/math.pi), GimbalDrone.scale)
            rect = img.get_rect()
            rect.center = (self.x,self.y)
            display.blit(img, rect)
            self.thrusterR.draw(self.x, self.y, self.angle, rang, display)
            self.thrusterL.draw(self.x, self.y, self.angle, lang, display)
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
                self.y - self.goal_positions[self.goal_counter%l][1],
                self.velocity[0], self.velocity[1], self.angle]#, self.ang_vel]

    def set_controls(self, controls = []):
        #controls = [.5,0,.1,0]
        self.lthrust = max(0, min(controls[0], 1))
        self.rthrust = max(0, min(controls[1], 1))
        self.rthrust_ang = max(-1, min(controls[2], 1))
        self.lthrust_ang = max(-1, min(controls[3], 1))

    class Thruster():
        def __init__(self, dist, do_draw = True):
            self.angle = -math.pi/2
            self.do_draw = do_draw
            self.dist = dist
            if self.do_draw:
                self.image = pygame.image.load("assets/thruster.png")
            self.ang_vel = 0.0

        def update(self, dt, ang_thrust, drone_angle):
            #self.ang_vel = ang_thrust * GimbalDrone.ANGTHRUST * dt
            #self.ang_vel = max(min(self.ang_vel, GimbalDrone.ANGVEL_MAX), -GimbalDrone.ANGVEL_MAX)
            self.angle += ang_thrust * GimbalDrone.ANGTHRUST * dt
            # Can't clamp because self.angle is already influenced by drone angle!!!!!
            self.angle = max(min(self.angle, (math.pi/4) - math.pi/2 + drone_angle), (-math.pi/4)- math.pi/2 + drone_angle)

        def get_angle(self):
            #print(self.angle)
            return self.angle

        def draw(self, droneX, droneY, droneAngle, angle, display):
            if self.do_draw:
                img = pygame.transform.rotozoom(self.image, -(self.angle*180/math.pi), GimbalDrone.scale)
                rect = img.get_rect()
                rect.center = (droneX + (self.dist * math.cos(droneAngle)),droneY + (self.dist * math.sin(droneAngle)))
                display.blit(img, rect)
