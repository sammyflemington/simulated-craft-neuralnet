import numpy
import pygame
import particle as p
class ParticleSystem():
    def __init__(self):
        self.parts = []
        self.part_surf = pygame.Surface((1920,1080))
        self.part_surf.set_alpha(100)

    def create_particle(self, particle: p.Particle):
        self.parts.append(particle)
        return particle

    def update(self, dt):
        for part in self.parts:
            # Remove dead parts
            if part.lifetime <= 0:
                self.parts.remove(part)
                del part
                continue
            part.update(dt)

    def draw(self, screen):
        self.part_surf.fill((0,0,0))
        for part in self.parts:
            part.draw(self.part_surf)

        screen.blit(self.part_surf, (0,0))
        #print(len(self.parts))
