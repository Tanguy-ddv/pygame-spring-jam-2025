# Built-ins
from abc import ABC, abstractmethod

# External
import pygame

# Scene class
class Scene(ABC):
    def start(self) -> None:
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.Event]) -> None:
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        pass

    def stop(self) -> None:
        pass