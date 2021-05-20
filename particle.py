import pygame

class Particle():
    def __init__(self, x, y, vx, vy, rad, rad_decay, lifetime, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = rad
        self.size_decay = rad_decay
        self.lifetime = lifetime
        self.color = color


    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.size -= self.size_decay * dt * 200
        self.lifetime -= dt

    def draw(self, display):
        pygame.draw.circle(display, self.color, (self.x,self.y),self.size)
