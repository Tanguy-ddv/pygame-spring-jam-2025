# External
import pygame

# Internal
from .. import EntityManager, PositionComponent, SurfaceComponent

class CameraSystem:
    def __init__(self):
        pass

    def draw(self, entity_manager: type[EntityManager], surface: pygame.Surface) -> None:
        entities = entity_manager.get_entities(
            PositionComponent,
            SurfaceComponent
        )

        for entity in entities:
            entity_position = entity.get_component(PositionComponent)
            entity_surface = entity.get_component(SurfaceComponent).surface

            surface.blit(entity_surface, entity_position)