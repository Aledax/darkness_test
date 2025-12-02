import pygame
from pygame.locals import *


class ColorScheme:

    def __init__(self,
                 color_bg: pygame.Color,
                 color_wall: pygame.Color,
                 color_player: pygame.Color):

        self.color_bg = color_bg
        self.color_wall = color_wall
        self.color_player = color_player