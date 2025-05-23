# Built-ins
import math

# External
import pygame
from pygame.locals import *

# Internal
from pygamelib import *
from entities import *
from assets import *

class Title(Scene):
    def __init__(self):
        # Scene manager
        self.scene_manager = SceneManager()

        # Background
        self.background_system = BackgroundSystem()
        self.camera = CameraSystem((1280, 720), (1280 / 2, 720 / 2))
        # Variables
        self.transition_timer = None
        self.prompt_colour = [0, 0, 0]
        self.time_elapsed = 0
        self.lerp_time = 0
        self.target = pygame.Vector2((1280 / 2, 720 / 2))
        self.original = self.target

    def start(self):
        sound:pygame.mixer.Sound = Sounds.get_sound("bgm")
        sound.set_volume(0.5)
        sound.play(-1)
    
    def handle_events(self, events, delta_time):
        for event in events:
            if event.type in [KEYDOWN, MOUSEBUTTONDOWN]:
                if self.transition_timer == None:
                    Sounds.get_sound("select").play()
                    self.transition_timer = Sounds.get_sound("select").get_length()
                    Sounds.get_sound("bgm").fadeout(500)

            elif event.type == MOUSEMOTION:
                 self.original = self.target
                 self.target = pygame.Vector2(1280 / 2, 720 / 2) - pygame.Vector2(event.pos) * 0.2
                 self.lerp_time = 0

    def update(self, delta_time):
        self.time_elapsed += delta_time
        self.lerp_time = min(1, self.lerp_time + delta_time)

        # self.camera.set_position(self.original + (self.target - self.original) * self.lerp_time)
        self.camera.set_position((self.camera.real_camera_x + 100 * delta_time, self.camera.real_camera_y + 100 * delta_time))
        self.background_system.update(self.camera, delta_time)

        if self.transition_timer != None:
            if self.transition_timer <= 0:
                self.scene_manager.set_scene("space")

            else:
                self.transition_timer -= delta_time
                for i, _ in enumerate(self.prompt_colour):
                    self.prompt_colour[i] = abs(math.sin(math.radians(self.time_elapsed * 800))) * 90

        else:
            for i, _ in enumerate(self.prompt_colour):
                self.prompt_colour[i] = abs(math.sin(math.radians(self.time_elapsed * 40))) * 60 + 100
        
    def draw(self, surface):
        # Draw bg
        self.background_system.draw(surface, self.camera, Images)

        # Draw Text
        prompt_image = Images.get_image("start prompt").copy()
        prompt_image.fill(self.prompt_colour, special_flags=BLEND_RGB_SUB)

        title_image = Images.get_image("title text")
        credit_image = Images.get_image("credit")

        surface.blit(prompt_image, (1280 / 2 - prompt_image.get_width() / 2, 650))
        surface.blit(title_image, (1280 / 2 - title_image.get_width() / 2, 50))
        surface.blit(credit_image, (1280 / 2 - credit_image.get_width() / 2, 720 - credit_image.get_height() - 5))
    
    def stop(self):
        return super().stop()

