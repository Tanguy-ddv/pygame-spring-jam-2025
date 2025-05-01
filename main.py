# Built-ins
import sys
import asyncio

# External
import pygame
from pygame.locals import *

# Internal
from pygamelib import *
from scenes import *

class Game:
    def __init__(self, screen_size, fps):
        self.screen_size = screen_size
        self.fps = fps

        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()

        self.scene_manager = SceneManager()
        self.scene_manager.register_scene(Title(), "title")
        self.scene_manager.register_scene(Space(), "space")
        self.scene_manager.set_scene("title")

    async def start(self):
        self.is_running = True

        while self.is_running:
            # Restart game
            if self.scene_manager.current_scene == "space" and  self.scene_manager.scene_dict[self.scene_manager.current_scene].restart:
                self.scene_manager.register_scene(Space(), "space")
                
            # Get delta time
            delta_time = self.clock.tick(self.fps) / 1000
            await asyncio.sleep(0)

            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.is_running = False

            self.scene_manager.handle_events(events)

            # Update frame
            self.scene_manager.update(delta_time)

            # Draw frame
            self.screen.fill((0, 0, 0))
            self.scene_manager.draw(self.screen)

            # Flip display
            pygame.display.flip()
            pygame.display.set_caption("fps: " + str(round(self.clock.get_fps())))

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