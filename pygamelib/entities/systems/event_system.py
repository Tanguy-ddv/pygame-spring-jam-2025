# External
import pygame

# Internal
from pygamelib.entities import Listener, EntityManager

class EventSystem:
    def handle_events(self, entity_manager: EntityManager, events: tuple[pygame.Event]):
        listeners = entity_manager.get_from_components(Listener)

        for event in events:
            for entity_id in listeners:
                listener: Listener = entity_manager.get_component(entity_id, Listener)

                if  event.type in listener.get_subjects():
                    for observer in listener.get_observers(event.type):
                        observer.handle_event(entity_manager, entity_id, event)