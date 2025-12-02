import sys
import pygame
from pygame.locals import *
from src.utils.pygameutils import *
from src.lib.wall import Wall
from src.lib.colorscheme import ColorScheme
from src.lib.map import Map
from src.lib.player import Player
from src.lib.fog import *
from src.lib.network.client import *


RESOLUTION = (600, 600)
WINDOW_SURFACE = pygame.display.set_mode(RESOLUTION)
FPS = 60

WALL_BORDER_THICKNESS = 20

COLOR_SCHEME = ColorScheme(
    color_bg=pygame.Color(65, 82, 84),
    color_wall=pygame.Color(30, 61, 65),
    color_player=pygame.Color(163, 203, 61)
)

MAP = Map(
    [
        Wall(0, 0, RESOLUTION[0], WALL_BORDER_THICKNESS),
        Wall(0, WALL_BORDER_THICKNESS, WALL_BORDER_THICKNESS, RESOLUTION[1] - 2 * WALL_BORDER_THICKNESS),
        Wall(RESOLUTION[0] - WALL_BORDER_THICKNESS, WALL_BORDER_THICKNESS, WALL_BORDER_THICKNESS, RESOLUTION[1] - 2 * WALL_BORDER_THICKNESS),
        Wall(0, RESOLUTION[1] - WALL_BORDER_THICKNESS, RESOLUTION[0], WALL_BORDER_THICKNESS),

        Wall(200, 200, 50, 50),
        Wall(350, 350, 50, 50),
        Wall(200, 350, 50, 50),
        Wall(350, 200, 50, 50)
    ],
    COLOR_SCHEME
)

PLAYER = Player(RESOLUTION[0] / 2, RESOLUTION[1] / 2)

KEYBIND_LEFT = K_LEFT
KEYBIND_RIGHT = K_RIGHT
KEYBIND_UP = K_UP
KEYBIND_DOWN = K_DOWN


class App:

    def __init__(self, window_surface: pygame.Surface, fps: int, color_scheme: ColorScheme, map: Map, player: Player):

        self.resolution = window_surface.get_size()
        self.window_surface = window_surface

        self.clock = pygame.time.Clock()
        self.fps = fps

        self.color_scheme = color_scheme
        self.map = map
        self.bg_surface = pygame.surface.Surface(self.resolution).convert_alpha()
        self.map.render(self.bg_surface)
        self.fog_surface = generate_fog_surface()

        self.player = player

        self.loop()

        pygame.quit()
        sys.exit()

    def update_gamestate(self, keys_pressed: list):

        direction = [0, 0]
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

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                    
    def render(self):

        bg_subsurface_rect = pygame.Rect(max(0, self.player.x - VISIBILITY_RADIUS),
                                            max(0, self.player.y - VISIBILITY_RADIUS),
                                            min([self.player.x + VISIBILITY_RADIUS, self.resolution[0] - (self.player.x - VISIBILITY_RADIUS), VISIBILITY_RADIUS * 2]),
                                            min([self.player.y + VISIBILITY_RADIUS, self.resolution[1] - (self.player.y - VISIBILITY_RADIUS), VISIBILITY_RADIUS * 2]))
        fog_rect = pygame.Rect(self.player.x - VISIBILITY_RADIUS,
                                self.player.y - VISIBILITY_RADIUS,
                                min(self.resolution[0] - self.player.x + VISIBILITY_RADIUS, VISIBILITY_RADIUS * 2),
                                min(self.resolution[1] - self.player.y + VISIBILITY_RADIUS, VISIBILITY_RADIUS * 2))
        self.window_surface.fill((0, 0, 0), (0, 0, *self.resolution))
        self.window_surface.blit(self.bg_surface.subsurface(bg_subsurface_rect), bg_subsurface_rect.topleft)
        self.player.render(self.window_surface, self.color_scheme.color_player)
        self.window_surface.blit(self.fog_surface, fog_rect.topleft)

    def loop(self):

        while True:

            self.update_gamestate(pygame.key.get_pressed())
            self.render()
                    
            pygame.display.update()
            self.clock.tick(self.fps)


if __name__ == '__main__':

    app = App(WINDOW_SURFACE, FPS, COLOR_SCHEME, MAP, PLAYER)