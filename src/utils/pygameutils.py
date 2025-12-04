import os
import math
import pygame
from pygame.locals import *
from pygame import gfxdraw
from typing import Tuple, List


def vector_add(v1: tuple, v2: tuple):

    return tuple([a + b for a, b in zip(v1, v2)])


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


def angle_2_vector(angle: float, magnitude: float):

    x = math.cos(angle) * magnitude
    y = math.sin(angle) * magnitude
    return (x, y)


def aacircle_filled(surface: pygame.Surface, x: int, y: int, radius: int, color: pygame.Color):

    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.aacircle(surface, x - 1, y, radius, color)
    gfxdraw.aacircle(surface, x, y - 1, radius, color)
    gfxdraw.aacircle(surface, x - 1, y - 1, radius, color)
    pygame.draw.circle(surface, color, (x, y), radius)


def generate_fog_surface(color: pygame.Color, radius: int):

    surface = pygame.surface.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for x in range(radius * 2):
        for y in range(radius * 2):
            distance_from_center = ((x - radius) ** 2 + (y - radius) ** 2) ** 0.5
            surface.set_at((x, y), (color.r, color.g, color.b, min(255, round(distance_from_center / radius * 255))))

    return surface


def brighten_color(color: pygame.Color, amount: int):

    h, s, l, a = color.hsla
    l = min(100, l + amount)
    brightened_color = pygame.Color(color)
    brightened_color.hsva = h, s, l, a
    return brightened_color


def load_image(path: str):

    return pygame.image.load(os.path.join('assets', 'images', path)).convert_alpha()


def load_animation(path_lambda: callable):

    index = 0
    frames = []
    while os.path.exists(os.path.join('assets', 'animations', path_lambda(index))):
        frames.append(pygame.image.load(os.path.join('assets', 'animations', path_lambda(index))).convert_alpha())
        index += 1
    return frames


def color_black_image(image: pygame.Surface, color: pygame.Color):

    colored_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    colored_image.fill((color.r, color.g, color.b, 255))
    alpha_image = pygame.surfarray.pixels_alpha(image)
    pygame.surfarray.pixels_alpha(colored_image)[:] = alpha_image[:]
    return colored_image


def blit_center(surface: pygame.Surface, image: pygame.Surface, position: tuple):

    rect = image.get_rect(center=(round(position[0]), round(position[1])))
    surface.blit(image, rect)


def aa_circle(surface: pygame.Surface, color: pygame.Color, center: Tuple[int, int], radius: int):
    
    solid_color = pygame.Color(color.r, color.g, color.b, 255)
    temp_surface = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
    gfxdraw.aacircle(temp_surface, radius + 1, radius + 1, radius, solid_color)
    gfxdraw.aacircle(temp_surface, radius, radius + 1, radius, solid_color)
    gfxdraw.aacircle(temp_surface, radius + 1, radius, radius, solid_color)
    gfxdraw.aacircle(temp_surface, radius, radius, radius, solid_color)
    pygame.draw.circle(temp_surface, solid_color, (radius + 1, radius + 1), radius)
    temp_surface.fill((255, 255, 255, color.a), special_flags=BLEND_RGBA_MULT)
    surface.blit(temp_surface, (center[0] - radius - 1, center[1] - radius - 1))


def aa_sector(surface: pygame.Surface, color: pygame.Color, center: Tuple[int, int], radius: float, inner_radius: float, start_angle: float, end_angle: float, angle_per_point: float = 0.05):
    
    steps = abs(math.ceil((end_angle - start_angle) / angle_per_point))
    is_reversed = end_angle < start_angle
    solid_color = pygame.Color(color.r, color.g, color.b, 255)
    temp_surface = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
    point_list = []
    inner_point_list = []
    for i in range(steps + 1):
        angle = start_angle + angle_per_point * i if not is_reversed else start_angle - angle_per_point * i
        x = round((radius) * math.cos(angle)) + radius + 1
        y = round((radius) * math.sin(angle)) + radius + 1
        inner_x = round((inner_radius) * math.cos(angle)) + radius + 1
        inner_y = round((inner_radius) * math.sin(angle)) + radius + 1
        point_list.append((x, y))
        inner_point_list.append((inner_x, inner_y))
    point_list += inner_point_list[::-1]
    if len(point_list) < 3:
        return
    
    gfxdraw.aapolygon(temp_surface, point_list, solid_color)
    pygame.draw.polygon(temp_surface, solid_color, point_list)
    temp_surface.fill((255, 255, 255, color.a), special_flags=BLEND_RGBA_MULT)
    surface.blit(temp_surface, (center[0] - radius - 1, center[1] - radius - 1))


def loading_sector(surface: pygame.Surface, color: pygame.Color, center: Tuple[int, int], radius: float, inner_radius: float, progress: float):
    
    start_angle = math.pi * 3 / 2
    end_angle = math.pi * 3 / 2 - math.pi * 2 * progress
    aa_sector(surface, color, center, radius, inner_radius, start_angle, end_angle)