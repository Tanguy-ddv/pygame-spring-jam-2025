# External
import pygame

class SurfaceComponent:
    def __init__(self, surface):
        self.surface = surface
        self.mask = pygame.mask.from_surface(self.surface)