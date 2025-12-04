import pygame
from pygame.locals import *
from typing import Tuple, List, Dict
from src.utils.pygameutils import *
from src.lib.colorscheme import ColorScheme


def generate_mine_surfaces(color_scheme: ColorScheme):
    base_mine_surface = pygame.transform.smoothscale(load_image('mine.png'), (Mine.ICON_RADIUS * 2, Mine.ICON_RADIUS * 2))
    return [{
        'dark': color_black_image(base_mine_surface.copy(), brighten_color(color, -15)),
        'light': color_black_image(base_mine_surface.copy(), brighten_color(color, 20))
    } for color in color_scheme.color_player_list]

def generate_mine_explosion_surfaces():
    explosion_surfaces = load_animation(lambda index: os.path.join('explosion', f'explosion_{index}.png'))
    resized_explosion_surfaces = [pygame.transform.smoothscale(frame, (round(Mine.EXPLOSION_VISUAL_RADIUS * 2 / Mine.EXPLOSION_HW_RATIO), Mine.EXPLOSION_VISUAL_RADIUS * 2)) for frame in explosion_surfaces]
    return resized_explosion_surfaces


class Mine:

    ICON_RADIUS = 12
    TRIGGER_RADIUS = 40
    EXPLOSION_RADIUS = 75
    EXPLOSION_VISUAL_RADIUS = 150
    EXPLOSION_HW_RATIO = 1.2
    LOAD_TIME_S = 1
    DETONATE_TIME_S = 0.4
    EXPLOSION_TIME_S = 0.66
    FLASH_INTERVAL_S = 0.05
    COOLDOWN_S = 5

    def __init__(self, player_id: int, position: Tuple[float, float]):

        self.player_id = player_id
        self.position = position
        
        self.triggered = False
        self.detonate_time = 0
        self.explosion_time = 0

    @property
    def detonated(self):
        return self.detonate_time == 0 and self.triggered

    @property
    def exploded(self):
        return self.explosion_time == 0 and self.triggered and self.detonate_time == 0

    @property
    def icon_rect(self):
        return pygame.Rect(
            round(self.position[0] - Mine.ICON_RADIUS),
            round(self.position[1] - Mine.ICON_RADIUS),
            Mine.ICON_RADIUS * 2,
            Mine.ICON_RADIUS * 2
        )
    
    @property
    def explosion_icon_rect(self):
        return pygame.Rect(
            round(self.position[0] - Mine.EXPLOSION_VISUAL_RADIUS / Mine.EXPLOSION_HW_RATIO),
            round(self.position[1] - Mine.EXPLOSION_VISUAL_RADIUS),
            Mine.EXPLOSION_VISUAL_RADIUS * 2 / Mine.EXPLOSION_HW_RATIO,
            Mine.EXPLOSION_VISUAL_RADIUS * 2
        )
    
    @staticmethod
    def from_dict(data: dict):
        mine = Mine(
            player_id=data['player_id'],
            position=tuple(data['position'])
        )
        mine.triggered = data.get('triggered', False)
        mine.detonate_time = data.get('detonate_time', 0)
        mine.explosion_time = data.get('explosion_time', 0)
        return mine
    
    def to_dict(self):
        return {
            'player_id': self.player_id,
            'position': self.position,
            'triggered': self.triggered,
            'detonate_time': self.detonate_time,
            'explosion_time': self.explosion_time
        }
    
    def trigger(self):

        self.detonate_time = Mine.DETONATE_TIME_S
        self.triggered = True

    def check_for_trigger(self, gamestate):

        for player in gamestate.players.values():
            if player.id != self.player_id and player.alive:
                dx = player.x - self.position[0]
                dy = player.y - self.position[1]
                distance_sq = dx * dx + dy * dy
                if distance_sq <= Mine.TRIGGER_RADIUS * Mine.TRIGGER_RADIUS:
                    self.trigger()
                    break

    def check_for_hits(self, gamestate):

        for player in gamestate.players.values():
            if player.id != self.player_id and player.alive:
                dx = player.x - self.position[0]
                dy = player.y - self.position[1]
                distance_sq = dx * dx + dy * dy
                if distance_sq <= Mine.EXPLOSION_RADIUS * Mine.EXPLOSION_RADIUS:
                    print('Mine hit player', player.id)
                    player.kill()
    
    def update(self, gamestate, dt_s: float):

        if self.triggered:
            if self.detonate_time > 0:
                self.detonate_time -= dt_s
                if self.detonate_time <= 0:
                    self.detonate_time = 0
                    self.explosion_time = Mine.EXPLOSION_TIME_S
                    self.check_for_hits(gamestate)
            elif self.explosion_time > 0:
                self.explosion_time = max(0, self.explosion_time - dt_s)
                if self.explosion_time == 0:
                    self.explosion_time = 0
        else:
            self.check_for_trigger(gamestate)

    def render_base(self, surface: pygame.Surface, visibility_rects: List[pygame.Rect], mine_surfaces: List[Dict[str, pygame.Surface]]):

        if (not self.triggered or self.detonate_time > 0) and any(rect.colliderect(self.icon_rect) for rect in visibility_rects):
            aa_circle(surface, pygame.Color(0, 0, 0, 20), (round(self.position[0]), round(self.position[1])), Mine.TRIGGER_RADIUS)
            if not self.triggered:
                shade = 'dark'
            else:
                shade = 'light' if int((Mine.DETONATE_TIME_S - self.detonate_time) / Mine.FLASH_INTERVAL_S) % 2 == 0 else 'dark'
            surface.blit(
                mine_surfaces[self.player_id][shade],
                self.icon_rect.topleft
            )

    def render_explosion(self, surface: pygame.Surface, visibility_rects: List[pygame.Rect], explosion_surfaces: List[pygame.Surface]):
        
        if self.triggered and self.explosion_time > 0 and any(rect.colliderect(self.explosion_icon_rect) for rect in visibility_rects):
            progress = 1.0 - (self.explosion_time / Mine.EXPLOSION_TIME_S)
            frame_index = int(progress * len(explosion_surfaces))
            surface.blit(
                explosion_surfaces[frame_index],
                self.explosion_icon_rect.topleft
            )