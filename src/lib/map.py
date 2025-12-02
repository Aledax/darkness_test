import pygame
from pygame.locals import *
from typing import List
from src.lib.wall import Wall
from src.lib.colorscheme import ColorScheme
from src.lib.player import Player


class Map:

    def __init__(self, walls: List[Wall], color_scheme: ColorScheme):

        self.walls = walls
        self.color_scheme = color_scheme

    def render(self, surface: pygame.Surface):

        surface.fill(self.color_scheme.color_bg)

        for wall in self.walls:
            wall.render(surface, self.color_scheme.color_wall)

    def resolve_player_wall_collisions(self, player: Player, direction: tuple):

        for wall in self.walls:
            wall.resolve_player_collision(player, direction)