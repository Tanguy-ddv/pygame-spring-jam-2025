# Built-ins

# External
import pygame
import math
from pygame.locals import *

# Internal
from pygamelib import *
from entities import *
from assets import *
from utils.constants import GAMEH_PER_REALSEC

class HUD:
    def __init__(self, fuel, balance):
        # Elements
        self.map = Map()
        self.log = Log()
        self.planet_interface = PlanetInterface(fuel, balance, self.log)
        self.manual = Manual()
        self.fuel_display = FuelDisplay()
        self.balance = BalanceDisplay()
        self.waypoint_markers = WaypointMarkers(40, 10)

    def handle_event(self, entity_manager, player_id, camera, event):
        if self.planet_interface.planet == None:
            self.map.handle_event(event)
            self.log.handle_event(event)

        self.planet_interface.handle_event(entity_manager, player_id, camera, event)
        self.manual.handle_event(event)

    def update(self, entity_manager: EntityManager, player_id: int, planet_ids: list[int], future_player_positions: list[tuple], pirate_handler: PirateHandler, camera, delta_time) -> None:
        self.map.update(entity_manager, player_id, planet_ids, future_player_positions, pirate_handler)
        self.manual.update(delta_time)
        self.log.update(delta_time)
        self.planet_interface.update(camera, delta_time)
        self.fuel_display.update(entity_manager, player_id, delta_time)
        self.waypoint_markers.update(entity_manager)
        self.waypoint_markers.set_waypoint_center(entity_manager.get_component(player_id, Position))
        self.waypoint_markers.set_max_distance_modifier(entity_manager.get_component(player_id, Scanner).view_distance_modifier)

        if self.planet_interface.planet != None:
            self.log.state = "planet view"

        else:
            self.log.state = "space"

        self.balance.update(entity_manager.get_component(player_id, Balance).credits)

    def draw(self, surface: pygame.surface.Surface, camera: CameraSystem):
        if self.planet_interface.enabled:
            self.planet_interface.draw(surface)
            self.log.draw(surface)
            self.balance.draw(surface, (self.planet_interface.board_x + self.planet_interface.width / 2 - self.balance.surface.get_width() / 2,
                                        self.planet_interface.board_y + 80))

            self.manual.draw(surface)

        elif self.map.fullscreened and self.map.map_mode != 0:
            self.map.draw(surface)

        else:
            self.map.draw(surface)
            self.log.draw(surface)
            self.fuel_display.draw(surface)
            self.manual.draw(surface)
            self.balance.draw(surface, (0, self.fuel_display.widget_size[1]))

        if self.planet_interface.enabled == False and (self.map.fullscreened == False or self.map.map_mode == 0):
            self.waypoint_markers.draw(surface, camera)

class FuelDisplay:
    def __init__(self):
        self.target_fuel_level = 1
        self.fuel_level = 1
        self.initial_fuel_level = 1

        self.time_elapsed = 0
        self.widget_center = (225, 25)
        self.widget_size = (500, 50)
        self.widget_rect = pygame.rect.Rect(self.widget_center[0] - self.widget_size[0] / 2, self.widget_center[1] - self.widget_size[1] / 2, self.widget_size[0], self.widget_size[1])
        self.color_a = [240, 240, 40]
        self.color = self.color_a.copy()
        self.render_time = 0
        self.text = Fonts.get_font("Body").render("POWER : 100%", True, "#222222")

    def update(self, entity_manager, player_id, delta_time):
        self.time_elapsed += delta_time

        fuel = entity_manager.get_component(player_id, Fuel)
        last_target = self.target_fuel_level

        self.target_fuel_level = fuel.fuel / fuel.max_fuel
        if last_target != self.target_fuel_level:
            self.time_elapsed = 0
            self.initial_fuel_level = self.fuel_level

        last_fuel = self.fuel_level
        self.fuel_level = min(self.target_fuel_level, self.initial_fuel_level + (self.target_fuel_level - self.initial_fuel_level) * abs(math.sin(math.radians(min(self.time_elapsed * 90, 90)))))

        if self.fuel_level != last_fuel:
            self.render_time += delta_time
            self.color[2] = 40 + abs(math.sin(math.radians(self.render_time * 90))) * 90
            self.text = Fonts.get_font("Body").render(f"POWER : {round(self.fuel_level * 100)}%", True, "#222222")

        else:
            self.render_time = 0
            self.color = self.color_a.copy()

    def draw(self, surface):
        pygame.draw.rect(surface, (125, 125, 125), self.widget_rect)

        fuel_bar_rect = self.widget_rect.copy()
        fuel_bar_rect.width *= self.fuel_level
        pygame.draw.rect(surface, self.color, fuel_bar_rect)
        color = self.color.copy()
        color[0] *= 0.95
        color[1] *= 0.95
        color[2] *= 0.95
        shade_rect = fuel_bar_rect.copy()
        shade_rect.height /= 2
        shade_rect.y += shade_rect.height 

        pygame.draw.rect(surface, color, shade_rect)

        text_pos = self.widget_rect.copy()
        text_pos.x = self.widget_rect.x + self.widget_size[0] / 2 - self.text.get_width() / 2
        text_pos.y = self.widget_rect.y + self.widget_size[1] / 2 - self.text.get_height() / 2
        surface.blit(self.text, text_pos)

class BalanceDisplay:
    def __init__(self):
        self.value = 0
        self.last_value = 0
        self.surface = None

        self._render_text()

    def _render_text(self):
        self.surface = Fonts.get_font("Small").render(
            f"BALANCE : ${self.value}",
            True,
            (150, 255, 150)
        )
    def update(self, new_value):
        self.value = new_value

        if self.last_value != self.value:
            self.last_value = self.value
            self._render_text()

    def draw(self, surface, offset):
        surface.blit(self.surface, offset)

class PlanetInterface:
    def __init__(self, fuel, balance, log):
        self.planet = None
        self.enabled = False
        self.dist = 40
        self.width = 1280 / 3
        self.height = 720 - self.dist * 2
        self.board_x = 1280 - self.dist - self.width
        self.board_y = self.dist
        self.zoom = 1
        self.active_tab = "missions"
        self.log = log

        self.fuel = fuel
        self.balance = balance
        
        with open("data/upgrades.json", "r") as file:
            self.upgrade_dict = json.load(file)

        self.surfaces = {key: self._render_text(key) for key in self.upgrade_dict}

    def _render_text(self, upgrade_name):
        font = Fonts.get_font("Small")
        level = self.upgrade_dict[upgrade_name]["level"]

        # Create surface
        surface = pygame.surface.Surface((1280 / 3, font.get_height() * 3.5), SRCALPHA)

        # Draw bg
        pygame.draw.rect(surface, (30, 30, 30), (0, 0, 1280 / 3, font.get_height() * 3.5), 0, 5)

        # if level + 1 >= len(self.upgrade_dict[upgrade_name]["prices"]):
        #     max_text = Images.get_image("maxed")
        #     surface.blit(max_text, (surface.get_width() / 2 - max_text.get_width() / 2, surface.get_height() / 2 - max_text.get_height() / 2))
        #     return surface
        
        desc = self.upgrade_dict[upgrade_name]["description"]

        # Upgrade title + cost
        if level + 1 >= len(self.upgrade_dict[upgrade_name]["prices"]) or self.upgrade_dict[upgrade_name]["prices"][level + 1] == 0:
            titletext = f"{upgrade_name} LV.{level + 1} : MAXED OUT" if upgrade_name != "recharge" else f"{upgrade_name} : ${0}"
            colour = (150 * 0.65, 255 * 0.65, 150 * 0.65)

        else:
            cost = self.upgrade_dict[upgrade_name]["prices"][level + 1]
            titletext = f"{upgrade_name} LV.{level + 1} : ${cost}" if upgrade_name != "recharge" else f"{upgrade_name} : ${cost}"
            colour = (150, 255, 150)

        title = font.render(
            titletext,
            True,
            colour
        )

        surface.blit(title, (0, 0))

        # Upgrade description
        if level + 1 >= len(self.upgrade_dict[upgrade_name]["prices"]) or self.upgrade_dict[upgrade_name]["prices"][level + 1] == 0:
            description = font.render(
                desc,
                True,
                (255 * 0.65, 255 * 0.65, 255 * 0.65)
            )

        else:
            description = font.render(
                desc,
                True,
                (255, 255, 255)
            )
    
        surface.blit(description, (0, title.get_height() + 5))

        # buy prompt
        if upgrade_name == "recharge" and self.upgrade_dict[upgrade_name]["prices"][level + 1] != 0:
            text = Images.get_image("buy")
            surface.blit(text, (1280 / 3 - text.get_width() - 8, font.get_height() * 3.5 - text.get_height() - 5))

        elif level + 1 < len(self.upgrade_dict[upgrade_name]["prices"]) and upgrade_name != "recharge":
            text = Images.get_image("upgrade")
            surface.blit(text, (1280 / 3 - text.get_width() - 8, font.get_height() * 3.5 - text.get_height() - 5))

        return surface

    def handle_event(self, entity_manager, player_id, camera, event):
        if self.planet == None:
            return
        
        if event.type == MOUSEBUTTONDOWN:
            tab1 = Images.get_image("mission tab text")
            tab2 = Images.get_image("shop tab text")
            tab3 = Images.get_image("leave tab text")

            if pygame.Rect((self.board_x + 4, self.board_y + 8, tab1.get_width() + 10, tab1.get_height() + 25)).collidepoint(event.pos):
                self.active_tab = "missions"
                return
            
            elif pygame.Rect((self.board_x + 4+  5 + tab1.get_width() + 10 + 2, self.board_y + 8, tab2.get_width() + 10, tab2.get_height() + 25)).collidepoint(event.pos):
                self.active_tab = "shop"
                return

            elif pygame.Rect((self.board_x + 4 + tab1.get_width() + 10 + 23 + 2 + tab2.get_width(), self.board_y + 8, tab3.get_width() + 16, tab3.get_height() + 25)).collidepoint(event.pos):
                self.active_tab = "missions"
                camera.selected_planet = None
                return
            
            elif self.active_tab == "missions":
                offsety = 0

                mission_list = list(self.planet.mission_dict.keys())
                mission_list.sort(key=lambda x: x.reward, reverse=False)

                for mission in mission_list:
                    board_x = 1280 - self.dist - self.width
                    board_y = self.dist
                    topleft = (board_x, board_y + offsety + self.height - self.planet.mission_dict[mission].get_height() - 4)
                    offsety -= self.planet.mission_dict[mission].get_height() + 2

                    if self.planet.mission_dict[mission].get_rect(topleft=topleft).collidepoint(event.pos):
                        if self.log.add_mission(mission) or 1:
                            self.planet.mission_dict.pop(mission)

                            mission = new_mission(self.planet.reputation, self.planet.name)
                            self.planet.mission_dict[mission] = self.planet._render_mission(mission)
                            Sounds.get_sound("accept_mission").play(fade_ms=500)

                        return
                    
            elif self.active_tab == "shop":
                offsety = 0

                for upgrade_name in list(self.upgrade_dict.keys())[::-1]:
                    board_x = 1280 - self.dist - self.width
                    board_y = self.dist
                    topleft = (board_x, board_y + offsety + self.height - self.surfaces[upgrade_name].get_height() - 4)
                    offsety -= self.surfaces[upgrade_name].get_height() + 2

                    if self.surfaces[upgrade_name].get_rect(topleft=topleft).collidepoint(event.pos):
                        # Attributes
                        level = self.upgrade_dict[upgrade_name]["level"]
                        if level + 1 >= len(self.upgrade_dict[upgrade_name]["prices"]):
                            return
                        
                        cost = self.upgrade_dict[upgrade_name]["prices"][level + 1]

                        # ON CLICK
                        if self.balance.credits < cost:
                            return # maybe play purchase failed sound
                        
                        # maybe play purchase success sound
                        Sounds.get_sound("purchase").play(fade_ms=500)

                        self.balance.credits -= cost
                        if upgrade_name == "recharge":
                            self.fuel.fuel = self.fuel.max_fuel
                            self.surfaces[upgrade_name] = self._render_text(upgrade_name)
                            
                            return

                        elif upgrade_name == "reputation":
                            entity_manager.get_component(player_id, Reputation).reward_modifier = self.upgrade_dict[upgrade_name]["values"][level + 1]

                        elif upgrade_name == "battery":
                            entity_manager.get_component(player_id, Fuel).max_fuel = self.upgrade_dict[upgrade_name]["values"][level + 1]
                            entity_manager.get_component(player_id, Fuel).fuel = self.upgrade_dict[upgrade_name]["values"][level + 1]

                        elif upgrade_name == "efficiency":
                            entity_manager.get_component(player_id, Fuel).efficiency = self.upgrade_dict[upgrade_name]["values"][level + 1]

                        elif upgrade_name == "fire-rate":
                            entity_manager.get_component(player_id, FireRate).fire_rate_modifier = self.upgrade_dict[upgrade_name]["values"][level + 1]

                        elif upgrade_name == "scanner":
                            entity_manager.get_component(player_id, Scanner).view_distance_modifier = self.upgrade_dict[upgrade_name]["values"][level + 1]

                        self.upgrade_dict[upgrade_name]["level"] += 1
                        self.surfaces[upgrade_name] = self._render_text(upgrade_name)

                        return

    def update(self, camera, delta_time):
        self.planet = camera.selected_planet
        self.zoom = camera.zoom
        self.enabled = self.planet != None

        self.upgrade_dict["recharge"]["prices"][0] = int((self.fuel.max_fuel - self.fuel.fuel) * 5)
        self.surfaces["recharge"] = self._render_text("recharge")

    def draw(self, surface):
        if not self.enabled:
            return
        
        # Draw selected body name
        text = Images.get_image(self.planet.name + " title")
        surface.blit(text, (1280 / 2 - text.get_width() / 2, 720 / 2 - self.planet.radius / self.zoom - 50))
        
        # Draw Planet Frame
        pygame.draw.rect(surface, (60, 60, 60), (self.board_x - 4, self.board_y, self.width + 8, self.height), 0, 10)

        # Draw Tabs
        pygame.draw.rect(surface, (40, 40, 40), (self.board_x , self.board_y + 4, self.width, 112), 0, 5)

        # Draw tab outline
        if self.active_tab == "missions":
            tab1 = Images.get_image("mission tab text")
            tab2 = Images.get_image("shop tab text inactive")

        else:
            tab1 = Images.get_image("mission tab text inactive")
            tab2 = Images.get_image("shop tab text")

        tab3 = Images.get_image("leave tab text")

        pygame.draw.rect(surface, (30, 30, 30), (self.board_x + 4, self.board_y + 8, tab1.get_width() + 10, tab1.get_height() + 25), 0, 5)
        surface.blit(tab1, (self.board_x + 9, self.board_y + 4 + 12.5 + 4))

        pygame.draw.rect(surface, (30, 30, 30), (self.board_x + 4+  5 + tab1.get_width() + 10 + 2, self.board_y + 8, tab2.get_width() + 10, tab2.get_height() + 25), 0, 5)
        surface.blit(tab2, (self.board_x + 9 + 5 + tab1.get_width() + 10 + 2, self.board_y + 4 + 12.5 + 4))

        pygame.draw.rect(surface, (30, 30, 30), (self.board_x + 4 + tab1.get_width() + 10 + 23 + 2 + tab2.get_width(), self.board_y + 8, tab3.get_width() + 16, tab3.get_height() + 25), 0, 5)
        surface.blit(tab3, (self.board_x + 9 + 23 + tab1.get_width() + 10 + 2 + tab2.get_width(), self.board_y + 4 + 12.5 + 4))

        pygame.draw.rect(surface, (30, 30, 30), (self.board_x + 4 , self.board_y + 4 + 70, self.width - 8, 38), 0, 5)

        if self.active_tab == "missions":
            # Draw mission bg
            pygame.draw.rect(surface, (40, 40, 40), (self.board_x - 2, self.board_y + 118, self.width + 4, self.height - 118 - 1), 0, 10)

            # Draw missions
            offsety = 0

            mission_list = list(self.planet.mission_dict.keys())
            mission_list.sort(key=lambda x: x.reward, reverse=False)

            for mission in mission_list:
                mission_image = self.planet.mission_dict[mission]
                surface.blit(mission_image, (self.board_x, self.board_y + offsety + self.height - mission_image.get_height() - 4))
                offsety -= mission_image.get_height() + 2

        else:
            # Draw shop bg
            pygame.draw.rect(surface, (40, 40, 40), (self.board_x - 2, self.board_y + 118, self.width + 4, self.height - 118 - 1), 0, 10)

            # Draw upgrades
            offsety = 0

            for upgrade_surface in list(self.surfaces.values())[::-1]:
                surface.blit(upgrade_surface, (self.board_x, self.board_y + offsety + self.height - upgrade_surface.get_height() - 4))
                offsety -= upgrade_surface.get_height() + 2

class Manual:
    def __init__(self):
        self.enabled = True # Keybind T opens manual for tutorial

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_t:
                self.enabled = not self.enabled

    def update(self, delta_time):
        pass

    def draw(self, surface:pygame.surface.Surface):
        if self.enabled:
            image = Images.get_image("manual")
            surface.blit(image, image.get_rect(centery = 586))

class Log:
    def __init__(self):
        self.enabled = True
        self.last_state = True
        self.mission_dict = {} # Keybind J toggles quest log sidebar (active missions) They should also include dist to objective
        self.distance = 400
        self.position = 0
        self.duration = .5 # Num seconds to appear / reappear
        self.time_elapsed = self.duration
        self.state = "space"

    def _render_mission(self, mission):
        font = Fonts.get_font("Small")
        surface = pygame.surface.Surface((400, font.get_height() * 5), SRCALPHA)

        if mission.type == "kill":
            text = font.render(
                f"-Eliminate {mission.max_amount} {mission.item}\n near {mission.destination} ({mission.amount}/{mission.max_amount})",
                True,
                (255, 255, 255)
            )

        elif mission.type == "delivery":
            text = font.render(
                f"-Deliver {mission.max_amount}{mission.unit} of\n {mission.item} to {mission.destination}\n",
                True,
                (255, 255, 255)
            )

        elif mission.type == "complete":
            text = font.render(
                f"-${mission.reward} reward\n at {mission.destination}",
                True,
                (150, 255, 150)
            )

        else:
            surface = self.mission_dict[mission]

        surface.blit(text, (0, 0))
        if mission.type in ["kill", "delivery"]:
            new_surface = font.render(
                f" [${mission.reward} REWARD]",
                True,
                (150, 255, 150)
            )

            surface.blit(new_surface, (0, text.get_height() + 4))

        return surface

    def add_mission(self, mission):
        if len(self.mission_dict) >= 1:
            return False
        
        self.mission_dict[mission] = self._render_mission(mission)
        return True
    
    def get_missions(self):
        return self.mission_dict.keys()
    
    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_j:
                self.last_state = self.enabled
                self.enabled = not self.enabled

    def update(self, delta_time):
        if self.enabled:
            self.time_elapsed = min(self.time_elapsed + delta_time, self.duration)

        else:
            self.time_elapsed = max(self.time_elapsed - delta_time, -self.duration)

        self.position = (self.distance / self.duration * self.time_elapsed) - self.distance
        for mission in self.mission_dict:
            if mission.type == "clear":
                self.mission_dict.pop(mission)

            elif mission.amount != mission.last_amount or mission.last_type != mission.type:
                self.mission_dict[mission] = self._render_mission(mission)

    def draw(self, surface):
        log_text = Images.get_image("log text")
        surface.blit(log_text, (self.position + 15 - 25 + log_text.get_width() / 2, 270 - log_text.get_height()))
        pygame.draw.rect(surface, (255, 255, 255), (self.position + 15, 270, log_text.get_width() * 2 - 50, 5))

        offsety = 0
        mission_list = list(self.mission_dict)
        mission_list.sort(key=lambda x: 0 if x.type == "complete" else 1)

        if mission_list == []:
            if self.state == "space":
                surface.blit(Images.get_image("empty log"), (self.position + 20, 300))

            elif self.state == "planet view":
                surface.blit(Images.get_image("empty log + planet view"), (self.position + 20, 300))

            return
        
        for mission in mission_list:
            if mission.type == "clear":
                continue

            surface.blit(self.mission_dict[mission], (self.position + 20, offsety + 300))
            offsety += self.mission_dict[mission].get_height() + 12

class Map:
    def __init__(self):
        self.map_surface = pygame.surface.Surface((1280, 720), pygame.SRCALPHA)
        self.map_surface_center = pygame.Vector2(self.map_surface.get_rect().size) / 2

        self.map_mode = 0
        self.last_mode = 1
        self.fullscreened = False
        self.panning = False

        self.zoom = 1.0
        self.lastpos = (0, 0)
        self.offset = pygame.Vector2(0, 0)

    def handle_event(self, event):
        if event.type == MOUSEWHEEL:
            if event.y == 1:
                self.set_zoom(self.zoom + 0.1)

            elif event.y == -1:
                self.set_zoom(self.zoom - 0.1)

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.panning = True
                self.last_pos = event.pos

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.panning = False

        elif event.type == KEYDOWN:
            self.key_pressed(event)

    def key_pressed(self, event):
            if event.key == K_UP:
                self.set_zoom(self.zoom + 0.1)

            elif event.key == K_DOWN:
                self.set_zoom(self.zoom - 0.1)

            elif event.key == K_m:
                if self.map_mode == 0:
                    self.set_mode(self.last_mode)

                else:
                    self.set_mode(0)

            elif event.key == K_TAB:
                self.fullscreened = not self.fullscreened
                self.set_zoom(1)

            elif event.key == K_v:
                if self.map_mode == 1:
                    self.set_mode(2)

                    self.last_mode = self.map_mode

                elif self.map_mode == 2:
                    self.set_mode(1)

                    self.last_mode = self.map_mode

            elif event.key == K_r:
                self.set_zoom(1)
                self.offset.x, self.offset.y = 0, 0

    def set_zoom(self, new_zoom):
        self.zoom = max(new_zoom, 0.01)
        # self.map_surface = pygame.surface.Surface((1280 * self.zoom, 720 * self.zoom))
        # self.map_surface_center = pygame.Vector2(self.map_surface.get_rect().size) / 2

    def set_mode(self, new_mode):
        self.map_mode = new_mode
        self.set_zoom(1)

    def update(self, entity_manager: EntityManager, player_id:int, planet_ids:list[int], future_player_positions:list[tuple], pirate_handler:PirateHandler):
        self.map_surface.fill((50, 50, 50))
        if self.fullscreened:
            if self.panning:
                new_pos = pygame.Vector2(pygame.mouse.get_pos())
                self.offset -= new_pos - self.last_pos
                self.last_pos = new_pos

            offset = self.offset

        else:
            offset = pygame.Vector2(0, 0)
            self.set_zoom(1)

        def calculate_scale(self, value:int|float):
            return value * self.zoom

        def calculate_on_map_position(self, position:pygame.Vector2):
            return self.map_surface_center[0] + calculate_scale(self, position.x / 460), self.map_surface_center[1] + calculate_scale(self, position.y / 460)

        if self.map_mode == 1:
            #pass one to draw orbit tracks
            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                if "moon" not in planet.kind:
                    center = self.map_surface_center - offset
                    if planet.orbits == None:
                        pygame.draw.circle(self.map_surface, "#FFFF00", center, calculate_scale(self, planet.dist / 460) + max(calculate_scale(self, planet.radius / 460), 5), 2)
                    else:
                        orbit:Planet = entity_manager.get_component(planet.orbits, Planet)
                        pygame.draw.circle(self.map_surface, "#DDDDDD", center, calculate_scale(self, planet.dist / 460) + calculate_scale(self, planet.radius / 460) + calculate_scale(self, orbit.radius / 460), 2)
            
            #pass two drawing moon orbit
            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                if  "moon"in planet.kind:
                    orbit:Planet = entity_manager.get_component(planet.orbits, Planet)
                    center = calculate_on_map_position(self, pygame.Vector2(orbit.x, orbit.y)) - offset
                    pygame.draw.circle(self.map_surface, "#DDDDDD", center, calculate_scale(self, planet.dist / 460) + calculate_scale(self, planet.radius / 460) + calculate_scale(self, orbit.radius / 460), 2)
            
            #pass three to draw planet positions

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)

                on_map_position = calculate_on_map_position(self, pygame.Vector2(planet.x, planet.y))

                if "moon" in planet.kind:
                    pygame.draw.circle(self.map_surface, (137, 35, 247), on_map_position - offset, max(calculate_scale(self, planet.radius / 460), 2))

                elif planet.kind == "sun":
                    pygame.draw.circle(self.map_surface, (255, 227, 84), on_map_position - offset, max(calculate_scale(self, planet.radius / 50), 3))

                else:
                    pygame.draw.circle(self.map_surface, (44, 95, 176), on_map_position - offset, max(calculate_scale(self, planet.radius / 460), 5))

            position:Position = entity_manager.get_component(player_id, Position)

            on_map_position = (self.map_surface_center[0] + calculate_scale(self, position.x / 460), self.map_surface_center[1] + calculate_scale(self, position.y / 460))

            pygame.draw.circle(self.map_surface, "#00FF00", on_map_position  - offset, min(max(calculate_scale(self, 4), 4), 4))

        elif self.map_mode == 2:
            player_position:Position = entity_manager.get_component(player_id, Position)

            # Draw bodies
            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                on_map_position = (self.map_surface_center[0] + calculate_scale(self, (planet.x - player_position.x) / 4), self.map_surface_center[1] + calculate_scale(self, (planet.y - player_position.y) / 4))

                if  "moon" in planet.kind:
                    pygame.draw.circle(self.map_surface, "#8923f7", on_map_position, calculate_scale(self, planet.radius / 4))

                elif planet.kind == "sun":
                    pygame.draw.circle(self.map_surface, "#ffe354", on_map_position, calculate_scale(self, planet.radius / 4))

                else:
                    pygame.draw.circle(self.map_surface, "#2c5fb0", on_map_position, calculate_scale(self, planet.radius / 4))

            # Draw predicted path
            for i in range(len(future_player_positions) - 2):
                p1 = future_player_positions[i]
                p2 = future_player_positions[i + 1]
                pygame.draw.line(self.map_surface, "#FFFFFF", (self.map_surface_center[0] + calculate_scale(self, (p1[0] - player_position.x) / 4), 
                                                                 self.map_surface_center[1] + calculate_scale(self, (p1[1] - player_position.y) / 4)),
                                                                (self.map_surface_center[0] + calculate_scale(self, (p2[0] - player_position.x) / 4), 
                                                                 self.map_surface_center[1] + calculate_scale(self, (p2[1] - player_position.y) / 4)))

            # Draw player
            pygame.draw.circle(self.map_surface, "#00FF00", self.map_surface_center, min(max(calculate_scale(self, 5), 5), 10))

            # Draw pirates
            for entity_id in pirate_handler.pirate_ids:
                pirate_position:Position = entity_manager.get_component(entity_id, Position)
                position = (self.map_surface_center[0] + calculate_scale(self, (pirate_position.x - player_position.x) / 4), self.map_surface_center[1] + calculate_scale(self, (pirate_position.y - player_position.y) / 4))
                pygame.draw.circle(self.map_surface, "#FF0000", position, min(max(calculate_scale(self, 5), 5), 10))

    def draw(self, surface: pygame.surface.Surface):
        if self.map_mode == 0:
            return
        
        elif self.map_mode == 1:
            self.draw_orbits()

        elif self.map_mode == 2:
            self.draw_planets()

        if self.fullscreened:
            self.draw_fullscreen(surface)

        else:
            self.draw_overlay(surface)

    def draw_orbits(self): # Move from update into here (maybe cache new values of planets in update and render here)
        pass

    def draw_planets(self): # Move from update into here (maybe cache new values of planets in update and render here)
        pass

    def draw_overlay(self, surface: pygame.surface.Surface):
        display_surface = pygame.transform.smoothscale(self.map_surface, (400, 225))
        surface.blit(display_surface, (surface.get_width() - display_surface.get_width(), 0))

    def draw_fullscreen(self, surface: pygame.surface.Surface):
        display_surface = pygame.transform.smoothscale(self.map_surface, (1280, 720))
        surface.blit(display_surface, display_surface.get_rect(center = (surface.get_width() - 1280 / 2, 720 / 2)))

class WaypointMarkers:
    def __init__(self, waypoint_distance:int, waypoint_length:int):
        self.waypoint_center = pygame.Vector2(0, 0)
        self.waypoint_distance = waypoint_distance
        self.waypoint_length = waypoint_length
        self.waypoints = []
        self.max_distance_modifier = 1

    def set_waypoint_center(self, waypoint_center:pygame.Vector2):
        self.waypoint_center = waypoint_center

    def set_max_distance_modifier(self, max_distance_modifier:int):
        self.max_distance_modifier = max_distance_modifier

    def update(self, entity_manager: EntityManager):
        self.waypoints.clear()
        
        entity_ids = entity_manager.get_from_components(Waypoint)
        for entity_id in entity_ids:
            self.waypoints.append(entity_manager.get_component(entity_id, Waypoint))

    def draw(self, surface: pygame.surface.Surface, camera: CameraSystem):
        for waypoint in self.waypoints:
            direction = math.atan2((waypoint.position.y - self.waypoint_center.y), (waypoint.position.x - self.waypoint_center.x))
            starting_position = camera.get_relative_position(self.waypoint_center)
            starting_position = (starting_position[0] + math.cos(direction) * self.waypoint_distance, starting_position[1] + math.sin(direction) * self.waypoint_distance)
            ending_position = (starting_position[0] + math.cos(direction) * self.waypoint_length, starting_position[1] + math.sin(direction) * self.waypoint_length)
            distance = math.sqrt((waypoint.position.x - self.waypoint_center.x) ** 2 + (waypoint.position.y - self.waypoint_center.y) ** 2)
            if waypoint.max_viewable_distance == None:
                fade = 1
            else:
                fade = (1 - (distance / waypoint.max_viewable_distance * self.max_distance_modifier))
                fade = min(max(fade, 0), 1)
            if fade != 0:
                color = (waypoint.color[0] * fade, waypoint.color[1] * fade, waypoint.color[2] * fade)
                pygame.draw.line(surface, color, starting_position, ending_position, 2)