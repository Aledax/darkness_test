import sys
import pygame
from pygame.locals import *
from src.utils.pygameutils import *
from src.lib.map import MAPS
from src.lib.network.protocol import *
from src.lib.player import *
from src.lib.eye import *
from src.lib.missile import *
from src.lib.mine import *


RESOLUTION = (600, 600)
WINDOW_SURFACE = pygame.display.set_mode(RESOLUTION)
FPS = 60
VISIBILITY_RADIUS = 100

KEYBIND_LEFT = K_a
KEYBIND_RIGHT = K_d
KEYBIND_UP = K_w
KEYBIND_DOWN = K_s
KEYBIND_EYE = K_e
KEYBIND_MINE = K_r


class PygameApp:

    def __init__(self):

        self.window_surface = WINDOW_SURFACE
        self.resolution = self.window_surface.get_size()

        self.clock = pygame.time.Clock()
        self.fps = FPS

    def initialize(self, client):

        self.client = client
        self.sockname = client.sockname

        self.last_gamestate = self.client.get_gamestate()
        self.player = None
        self.map = MAPS[self.last_gamestate.map_name]
        self.color_scheme = self.map.color_scheme
        
        self.bg_surface = pygame.surface.Surface(self.resolution, SRCALPHA).convert_alpha()
        self.mg_surface = pygame.surface.Surface(self.resolution, SRCALPHA).convert_alpha()
        self.map.render(self.bg_surface, self.mg_surface)

        self.player_fog_surface = generate_player_fog_surface()
        self.eye_fog_surface = generate_eye_fog_surface()
        self.eye_surfaces = generate_eye_surfaces(self.color_scheme)
        self.mine_surfaces = generate_mine_surfaces(self.color_scheme)
        self.mine_explosion_surfaces = generate_mine_explosion_surfaces()
        self.missile_surfaces = generate_missile_surfaces(self.color_scheme)
        self.missile_explosion_surfaces = generate_missile_explosion_surfaces()

        self.loop()

    def quit(self):

        pygame.quit()
        sys.exit()

    def handle_input(self, keys_pressed: list, aiming_destination: Tuple[int, int]):

        direction = [0, 0]
        if self.player.loading == Player.LOADING_TYPE_NONE:
            if keys_pressed[KEYBIND_LEFT]:
                direction[0] -= 1
            if keys_pressed[KEYBIND_RIGHT]:
                direction[0] += 1
            if keys_pressed[KEYBIND_UP]:
                direction[1] -= 1
            if keys_pressed[KEYBIND_DOWN]:
                direction[1] += 1

        angle = vector_2_angle(tuple(direction))
        if angle is not None:
            self.player.move_by(vector_2_angle(direction), 1.0 / self.fps)
            self.map.resolve_player_wall_collisions(self.player, tuple(direction))
            self.client.send_message(MSG_CODE_POSITION, {'x': self.player.x, 'y': self.player.y})

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.quit()
            elif event.type == KEYDOWN or event.type == KEYUP:
                is_keydown = event.type == KEYDOWN
                if event.key == KEYBIND_EYE and self.player.loading in [Player.LOADING_TYPE_NONE, Player.LOADING_TYPE_EYE]:
                    self.player.set_loading_client(Player.LOADING_TYPE_EYE if is_keydown else Player.LOADING_TYPE_NONE)
                    self.client.send_message(MSG_CODE_LOAD, {'loading': self.player.loading})
                elif event.key == KEYBIND_MINE and self.player.loading in [Player.LOADING_TYPE_NONE, Player.LOADING_TYPE_MINE]:
                    self.player.set_loading_client(Player.LOADING_TYPE_MINE if is_keydown else Player.LOADING_TYPE_NONE)
                    self.client.send_message(MSG_CODE_LOAD, {'loading': self.player.loading})
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    new_missile = self.player.add_missile_client(aiming_destination)
                    if new_missile is not None:
                        self.client.send_message(MSG_CODE_ADD_MISSILE, new_missile.to_dict())
                    
    def render(self, aiming_destination: Tuple[int, int]):

        self.window_surface.set_clip(None)
        self.window_surface.fill((0, 0, 0), (0, 0, *self.resolution))
        self.fog_surface = pygame.surface.Surface(self.resolution).convert_alpha()

        visibility_rects = [self.player.visibility_rect]

        for eye in self.player.eyes:
            visibility_rects.append(eye.visibility_rect)

        for visibility_rect in visibility_rects:
            self.window_surface.set_clip(visibility_rect)
            self.window_surface.blit(self.bg_surface, (0, 0))

        self.window_surface.set_clip(None)

        for player in self.last_gamestate.players.values():
            for mine in player.mines:
                mine.render_base(self.window_surface, visibility_rects, self.mine_surfaces)
            for eye in player.eyes:
                eye.render(self.window_surface, visibility_rects, self.eye_surfaces)

        for visibility_rect in visibility_rects:
            self.window_surface.set_clip(visibility_rect)
            self.window_surface.blit(self.mg_surface, (0, 0))
        self.window_surface.set_clip(None)

        for player in self.last_gamestate.players.values():
            player.render(self.window_surface, visibility_rects, self.color_scheme)

        for player in self.last_gamestate.players.values():
            for mine in player.mines:
                mine.render_explosion(self.window_surface, visibility_rects, self.mine_explosion_surfaces)
            for missile in player.missiles:
                missile.render(self.window_surface, visibility_rects, self.missile_surfaces, self.missile_explosion_surfaces)

        self.player.render_fog(self.fog_surface, self.player_fog_surface)
        for eye in self.player.eyes:
            eye.render_fog(self.fog_surface, self.eye_fog_surface)
        self.window_surface.blit(self.fog_surface, (0, 0))

        if self.player.alive:
            pygame.draw.circle(self.window_surface, (255, 0, 0), aiming_destination, 5)

    def loop(self):

        while True:

            new_gamestate = self.client.get_gamestate()
            if new_gamestate != None:
                self.last_gamestate = new_gamestate
                self.client.reset_gamestate_updated()
                self.player = self.last_gamestate.players.get(self.sockname, None)

            if self.player is None:
                continue

            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()

            aiming_destination = vector_add(angle_2_vector(
                vector_2_angle((
                    mouse_pos[0] - self.player.x,
                    mouse_pos[1] - self.player.y
                )),
                Missile.DESTINATION_DISTANCE
            ), self.player.position)

            self.handle_input(keys, aiming_destination)
            self.render(aiming_destination)
                    
            pygame.display.update()
            self.clock.tick(self.fps)
