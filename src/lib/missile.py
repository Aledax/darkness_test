import os
import pygame
from pygame.locals import *
from typing import Tuple, List
from src.utils.pygameutils import *
from src.lib.colorscheme import ColorScheme


def generate_missile_surfaces(color_scheme: ColorScheme):
    base_missile_surface = pygame.transform.smoothscale(load_image('missile.png'), (Missile.RADIUS * 2, Missile.RADIUS * 2))
    return [color_black_image(base_missile_surface.copy(), brighten_color(color, 100)) for color in color_scheme.color_player_list]

def generate_missile_explosion_surfaces():
    explosion_surfaces = load_animation(lambda index: os.path.join('explosion', f'explosion_{index}.png'))
    resized_explosion_surfaces = [pygame.transform.smoothscale(frame, (round(Missile.EXPLOSION_VISUAL_RADIUS * 2 / Missile.EXPLOSION_HW_RATIO), Missile.EXPLOSION_VISUAL_RADIUS * 2)) for frame in explosion_surfaces]
    return resized_explosion_surfaces


class Missile:

    RADIUS = 15
    EXPLOSION_VISUAL_RADIUS = 150
    EXPLOSION_RADIUS = 75
    EXPLOSION_HW_RATIO = 1.2
    TRAVEL_TIME_S = 0.5
    EXPLOSION_TIME_S = 0.66
    DESTINATION_DISTANCE = 250
    COOLDOWN_S = 0.7

    def __init__(self, player_id: int, origin: Tuple[float, float], destination: Tuple[float, float]):
        
        self.player_id = player_id
        self.origin = origin
        self.destination = destination

        self.travel_time = Missile.TRAVEL_TIME_S
        self.explosion_time = Missile.EXPLOSION_TIME_S
        self.just_detonated = False

    @property
    def landed(self):
        return self.travel_time <= 0
    
    @property
    def exploded(self):
        return self.explosion_time <= 0
    
    @property
    def current_position(self):
        if self.travel_time > 0:
            progress = 1 - (self.travel_time / Missile.TRAVEL_TIME_S)
            x = self.origin[0] + (self.destination[0] - self.origin[0]) * progress
            y = self.origin[1] + (self.destination[1] - self.origin[1]) * progress
            return (x, y)
        return self.destination
    
    @property
    def icon_rect(self):
        x, y = self.current_position
        return pygame.Rect(
            round((x - Missile.RADIUS)),
            round(y - Missile.RADIUS),
            Missile.RADIUS * 2,
            Missile.RADIUS * 2
        )
    
    @property
    def explosion_icon_rect(self):
        return pygame.Rect(
            round(self.destination[0] - Missile.EXPLOSION_VISUAL_RADIUS / Missile.EXPLOSION_HW_RATIO),
            round(self.destination[1] - Missile.EXPLOSION_VISUAL_RADIUS),
            Missile.EXPLOSION_VISUAL_RADIUS * 2 / Missile.EXPLOSION_HW_RATIO,
            Missile.EXPLOSION_VISUAL_RADIUS * 2
        )

    @staticmethod
    def from_dict(data: dict):
        missile = Missile(
            player_id=data['player_id'],
            origin=tuple(data['origin']),
            destination=tuple(data['destination'])
        )
        missile.travel_time = data.get('travel_time', 0)
        missile.explosion_time = data.get('explosion_time', 0)
        return missile
    
    def to_dict(self):
        return {
            'player_id': self.player_id,
            'origin': self.origin,
            'destination': self.destination,
            'travel_time': self.travel_time,
            'explosion_time': self.explosion_time
        }
    
    def update(self, dt_s: float):

        if self.travel_time > 0:
            self.travel_time -= dt_s
            if self.travel_time < 0:
                self.explosion_time += self.travel_time
                self.travel_time = 0
                self.just_detonated = True

        elif self.explosion_time > 0:
            self.explosion_time -= dt_s
            if self.explosion_time < 0:
                self.explosion_time = 0

    def check_for_hits(self, gamestate):

        if not self.just_detonated:
            return []

        self.just_detonated = False
        hit_players = []
        for peername, player in gamestate.players.items():
            if player.id != self.player_id and player.alive:
                dx = player.x - self.destination[0]
                dy = player.y - self.destination[1]
                distance_sq = dx * dx + dy * dy
                if distance_sq <= Missile.EXPLOSION_RADIUS * Missile.EXPLOSION_RADIUS:
                    hit_players.append(peername)
        return hit_players

    def render(self, surface: pygame.Surface, visibility_rects: List[pygame.Rect], missile_surfaces: List[pygame.Surface], explosion_surfaces: List[pygame.Surface]):

        if self.travel_time > 0 and any(rect.colliderect(self.icon_rect) for rect in visibility_rects):
            surface.blit(
                missile_surfaces[self.player_id],
                self.icon_rect.topleft
            )
        elif self.landed and self.explosion_time > 0 and any(rect.colliderect(self.explosion_icon_rect) for rect in visibility_rects):
            progress = 1.0 - (self.explosion_time / Missile.EXPLOSION_TIME_S)
            frame_index = int(progress * len(explosion_surfaces))
            surface.blit(
                explosion_surfaces[frame_index],
                self.explosion_icon_rect.topleft
            )