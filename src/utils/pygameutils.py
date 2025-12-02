import math
import pygame
from pygame.locals import *
from pygame import gfxdraw


def vector_2_angle(v: tuple):

    if v == (0, 0):
        return None
    if v[0] == 0:
        if v[1] > 0:
            return math.pi / 2
        return 3 * math.pi / 2
    if v[0] > 0:
        return math.atan(v[1] / v[0])
    return math.pi + math.atan(v[1] / v[0])


def aacircle_filled(surface: pygame.Surface, x: int, y: int, radius: int, color: pygame.Color):

    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.aacircle(surface, x - 1, y, radius, color)
    gfxdraw.aacircle(surface, x, y - 1, radius, color)
    gfxdraw.aacircle(surface, x - 1, y - 1, radius, color)
    pygame.draw.circle(surface, color, (x, y), radius)