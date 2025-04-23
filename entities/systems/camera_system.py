# External
import pygame

# Internal
from entities import *

#real camera position -> camera position without rounding
#camera position -> camera position with rounding
class CameraSystem:
    def __init__(self, screen_size: tuple, starting_position: tuple):
        self.screen_size = screen_size
        self.relative_offset = (screen_size[0] / 2, screen_size[1] / 2)
        self.real_camera_x, self.real_camera_y = starting_position

    @property
    def camera_x(self):
        return round(self.real_camera_x)
    
    @property
    def camera_y(self):
        return round(self.real_camera_y)

    def get_relative_position(self, position: tuple):
        return (position[0] - self.camera_x + self.relative_offset[0], position[1] - self.camera_y + self.relative_offset[1])
    
    def get_bounding_box(self, padding: int):
        return (self.camera_x - self.relative_offset[0] - padding, self.camera_y - self.relative_offset[1] - padding, 
                self.camera_x + self.relative_offset[0] + padding, self.camera_y + self.relative_offset[1] + padding)
    
    def set_position(self, position: tuple):
        self.real_camera_x, self.real_camera_y = position

    def draw(self, display_surface, entity_manager):
        entity_ids = entity_manager.get_from_components(pygame.Surface, Position)

        for entity_id in entity_ids:
            surface = entity_manager.get_component(entity_id, pygame.Surface)
            position = entity_manager.get_component(entity_id, Position)

            display_surface.blit(surface, position - (self.camera_x, self.camera_y) + self.relative_offset - pygame.Vector2(surface.get_rect().size) / 2)