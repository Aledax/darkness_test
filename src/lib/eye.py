import pygame
from pygame.locals import *
from typing import List
from src.utils.pygameutils import *
from src.lib.colorscheme import ColorScheme


def generate_eye_surfaces(color_scheme: ColorScheme):
    base_eye_surface = pygame.transform.smoothscale(load_image('eye.png'), (Eye.RADIUS * 2, Eye.RADIUS * 2))
    return [color_black_image(base_eye_surface.copy(), brighten_color(color, 100)) for color in color_scheme.color_player_list]

def generate_eye_fog_surface():
    return generate_fog_surface(pygame.Color(0, 0, 0), Eye.VISIBILITY_RADIUS)


class Eye:

    RADIUS = 12
    VISIBILITY_RADIUS = 120
    LIFETIME_S = 10
    LOAD_TIME_S = 1
    COOLDOWN_S = 20
    FOG_BRIGHTNESS_CHANGE_RATE = 2

    def __init__(self, player_id: int, x: float, y: float):

        self.player_id = player_id
        self.x = x
        self.y = y

        self.life = Eye.LIFETIME_S
        self.fog_brightness = 0

    @property
    def alive(self):
        return self.life > 0

    @property
    def icon_rect(self):
        return pygame.Rect(
            round(self.x - Eye.RADIUS),
            round(self.y - Eye.RADIUS),
            Eye.RADIUS * 2,
            Eye.RADIUS * 2
        )
    
    @property
    def visibility_rect(self):
        return pygame.Rect(
            round(self.x - Eye.VISIBILITY_RADIUS),
            round(self.y - Eye.VISIBILITY_RADIUS),
            Eye.VISIBILITY_RADIUS * 2,
            Eye.VISIBILITY_RADIUS * 2
        )
    
    @staticmethod
    def from_dict(data: dict):
        eye = Eye(
            player_id=data['player_id'],
            x=data['x'],
            y=data['y']
        )
        eye.life = data.get('life', Eye.LIFETIME_S)
        eye.fog_brightness = data.get('fog_brightness', 0)
        return eye
    
    def to_dict(self):
        return {
            'player_id': self.player_id,
            'x': self.x,
            'y': self.y,
            'life': self.life,
            'fog_brightness': self.fog_brightness
        }
    
    def update(self, gamestate, dt_s: float):

        if self.life > 0:
            self.life -= dt_s
            if self.life < 0:
                self.life = 0

        fog_change_time = 1.0 / Eye.FOG_BRIGHTNESS_CHANGE_RATE
        if self.life < fog_change_time:
            self.fog_brightness = self.life / fog_change_time
        elif Eye.LIFETIME_S - self.life < fog_change_time:
            self.fog_brightness = (Eye.LIFETIME_S - self.life) / fog_change_time
        else:
            self.fog_brightness = 1.0
    
    def render(self, surface: pygame.Surface, visibility_rects: List[pygame.Rect], eye_surfaces: List[pygame.Surface]):

        if any(self.visibility_rect.colliderect(visibility_rect) for visibility_rect in visibility_rects):
            surface.blit(
                eye_surfaces[self.player_id],
                self.icon_rect.topleft
            )
            loading_sector(
                surface,
                pygame.Color(0, 0, 0, 50),
                (round(self.x), round(self.y)),
                20, 16,
                self.life / Eye.LIFETIME_S
            )

    def render_fog(self, surface: pygame.Surface, fog_surface: pygame.Surface):

        new_fog_surface = fog_surface.copy()
        alpha_value = 255 - int(self.fog_brightness * 255)
        new_fog_surface.fill((0, 0, 0, alpha_value), special_flags=BLEND_RGBA_MAX)
        surface.blit(new_fog_surface, self.visibility_rect.topleft, special_flags=BLEND_RGBA_MIN)