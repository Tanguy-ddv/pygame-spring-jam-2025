# Built-ins
import sys
import asyncio

# External
import pygame
from pygame.locals import *

# Internal
from scenes import *
from entities import *
from resources import *
from utils import *

class Game:
    def __init__(self, screen_size, fps):
        self.screen_size = screen_size
        self.fps = fps

        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.scene_manager = SceneManager()

    async def start(self):
        self.is_running = True

        while self.is_running:
            # Get delta time
            delta_time = self.clock.tick(self.fps) / 1000
            await asyncio.sleep(0)

            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.is_running = False

            # Update frame
            self.scene_manager.update(delta_time)

            # Draw frame
            self.screen.fill((60, 60, 60))
            self.scene_manager.draw(self.screen)

            # Flip display
            pygame.display.flip()

        self.stop()

    def stop(self):
        pygame.quit()
        sys.exit()

# Entry point
if __name__ == "__main__":
    game = Game(
        screen_size=(1280, 720),
        fps=0
    )

    asyncio.run(game.start())