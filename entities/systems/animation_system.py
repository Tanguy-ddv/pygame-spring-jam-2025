# External
import pygame

# Internal
from pygamelib import *
from entities import *
from assets import *

class AnimationSystem:
    def draw(self, display_surface: pygame.Surface, entity_manager: EntityManager, camera) -> None:
        entity_ids = entity_manager.get_from_components(
            Animator,
            Position
        )

        for entity_id in entity_ids:
            animator = entity_manager.get_component(entity_id, Animator)
            position = entity_manager.get_component(entity_id, Position)

            for animation, frame in animator.animation_stack.items():
                surface = Animations.get_animation(animation, frame)

                if entity_manager.has_component(entity_id, Rotation):
                    rotation = entity_manager.get_component(entity_id, Rotation)
                    surface = pygame.transform.rotate(surface, rotation.angle - 90)

                display_surface.blit(surface, position - (camera.camera_x, camera.camera_y) + camera.relative_offset - pygame.Vector2(surface.get_rect().size) / 2)
                animator.animation_stack[animation] = frame + 1
