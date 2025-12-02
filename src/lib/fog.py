import pygame
from pygame.locals import *


VISIBILITY_RADIUS = 100


def generate_fog_surface():

    surface = pygame.surface.Surface((VISIBILITY_RADIUS * 2, VISIBILITY_RADIUS * 2), pygame.SRCALPHA)
    for x in range(VISIBILITY_RADIUS * 2):
        for y in range(VISIBILITY_RADIUS * 2):
            distance_from_center = ((x - VISIBILITY_RADIUS) ** 2 + (y - VISIBILITY_RADIUS) ** 2) ** 0.5
            surface.set_at((x, y), (0, 0, 0, min(255, round(distance_from_center / VISIBILITY_RADIUS * 255))))

    return surface