# External
import pygame
from pygame.locals import *

# Internal
from entities import *

#real camera position -> camera position without rounding
#camera position -> camera position with rounding
class CameraSystem:
    def __init__(self, screen_size: tuple, starting_position: tuple):
        self.screen_size = pygame.Vector2(screen_size)
        self.internal_surface = pygame.surface.Surface(self.screen_size)
        self.relative_offset = (self.internal_surface.get_size()[0] / 2, self.internal_surface.get_size()[1] / 2)
        self.real_camera_x, self.real_camera_y = starting_position
        self.selected_planet = None
        self.changed = False
        self.zoom = 1

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
    
    def get_surface(self):
        return self.internal_surface
    
    def set_position(self, position: tuple):
        self.real_camera_x, self.real_camera_y = position

    def set_zoom(self, new_zoom):
        if new_zoom == self.zoom:
            return
        
        self.zoom = new_zoom
        self.internal_surface = pygame.surface.Surface(self.screen_size * self.zoom)
        self.relative_offset = (self.internal_surface.get_size()[0] / 2, self.internal_surface.get_size()[1] / 2)

    def update(self, entity_manager, player_id, delta_time):
        self.internal_surface.fill((0, 0, 0))
        if self.selected_planet == None:
            if not entity_manager.has_component(player_id, Simulate):
                entity_manager.add_component(player_id, Simulate())

            self.set_position(entity_manager.get_component(player_id, Position))
            self.set_zoom(1)

        else:
            if entity_manager.has_component(player_id, Simulate):
                entity_manager.remove_component(player_id, Simulate)

            self.set_position((self.selected_planet.x, self.selected_planet.y))

            if self.selected_planet.kind == "moon":
                self.set_zoom(1.25)

            else:
                self.set_zoom(1.5)

    def draw(self, entity_manager):
        entity_ids = entity_manager.get_from_components(pygame.surface.Surface, Position)

        for entity_id in entity_ids:
            if entity_manager.has_component(entity_id, Dying):
                continue
            
            surface = entity_manager.get_component(entity_id, pygame.surface.Surface)
            position = entity_manager.get_component(entity_id, Position)
            self.get_surface().blit(surface, position - (self.camera_x, self.camera_y) + self.relative_offset - pygame.Vector2(surface.get_rect().size) / 2)