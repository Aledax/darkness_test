import math
import pygame
from pygame.locals import *
from typing import Tuple, List
from src.utils.pygameutils import *
from src.lib.colorscheme import ColorScheme
from src.lib.eye import Eye
from src.lib.missile import Missile
from src.lib.mine import Mine


def generate_player_fog_surface():
    return generate_fog_surface(pygame.Color(0, 0, 0), Player.VISIBILITY_RADIUS)


class Player:

    RADIUS = 10
    VISIBILITY_RADIUS = 100
    SPEED = 200
    RESPAWN_TIME = 10
    FOG_BRIGHTNESS_CHANGE_RATE = 2

    LOADING_TYPE_NONE = 0
    LOADING_TYPE_EYE = 1
    LOADING_TYPE_MINE = 2
    
    def __init__(self, id: int, x: float, y: float):

        self.id = id
        self.x = x
        self.y = y

        self.spawnpoint = (x, y)
        self.eye_cooldown = 0
        self.mine_cooldown = 0
        self.missile_cooldown = 0
        self.ammo = 100
        self.loading = Player.LOADING_TYPE_NONE
        self.load_time = 0

        self.respawn_timer = 0
        self.fog_brightness = 0

        self.eyes = []
        self.mines = []
        self.missiles = []
        
    @property
    def r(self):
        return Player.RADIUS
    
    @property
    def r_squared(self):
        return Player.RADIUS ** 2

    @property
    def position(self):
        return (self.x, self.y)
    
    @property
    def left(self):
        return self.x - Player.RADIUS
    
    @property
    def right(self):
        return self.x + Player.RADIUS
    
    @property
    def top(self):
        return self.y - Player.RADIUS
    
    @property
    def bottom(self):
        return self.y + Player.RADIUS
    
    @property
    def rect(self):
        return pygame.Rect(round(self.left), round(self.top), self.r * 2, self.r * 2)
    
    @property
    def visibility_rect(self):
        return pygame.Rect(
            round(self.x - Player.VISIBILITY_RADIUS),
            round(self.y - Player.VISIBILITY_RADIUS),
            Player.VISIBILITY_RADIUS * 2,
            Player.VISIBILITY_RADIUS * 2
        )
    
    @property
    def alive(self):
        return self.respawn_timer <= 0
    
    @property
    def loading_time_required(self):
        if self.loading == Player.LOADING_TYPE_EYE:
            return Eye.LOAD_TIME_S
        elif self.loading == Player.LOADING_TYPE_MINE:
            return Mine.LOAD_TIME_S
        else:
            return 0
    
    @staticmethod
    def from_dict(data: dict):
        player = Player(
            id=data['id'],
            x=data['x'],
            y=data['y'],
        )
        player.spawnpoint = data.get('spawnpoint', (0, 0))
        player.eye_cooldown = data.get('eye_cooldown', 0)
        player.mine_cooldown = data.get('mine_cooldown', 0)
        player.missile_cooldown = data.get('missile_cooldown', 0)
        player.ammo = data.get('ammo', 0)
        player.loading = data.get('loading', Player.LOADING_TYPE_NONE)
        player.load_time = data.get('load_time', 0)
        player.respawn_timer = data.get('respawn_timer', 0)
        player.fog_brightness = data.get('fog_brightness', 0)
        player.eyes = [Eye.from_dict(eye_data) for eye_data in data.get('eyes', [])]
        player.mines = [Mine.from_dict(mine_data) for mine_data in data.get('mines', [])]
        player.missiles = [Missile.from_dict(missile_data) for missile_data in data.get('missiles', [])]
        return player
    
    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'spawnpoint': self.spawnpoint,
            'eye_cooldown': self.eye_cooldown,
            'mine_cooldown': self.mine_cooldown,
            'missile_cooldown': self.missile_cooldown,
            'ammo': self.ammo,
            'loading': self.loading,
            'load_time': self.load_time,
            'respawn_timer': self.respawn_timer,
            'fog_brightness': self.fog_brightness,
            'eyes': [eye.to_dict() for eye in self.eyes],
            'mines': [mine.to_dict() for mine in self.mines],
            'missiles': [missile.to_dict() for missile in self.missiles]
        }
    
    def move_by(self, angle_radians, dt):

        if not self.alive:
            return

        new_x = self.x + math.cos(angle_radians) * Player.SPEED * dt
        new_y = self.y + math.sin(angle_radians) * Player.SPEED * dt

        self.x, self.y = new_x, new_y

    def move_to(self, position):

        if not self.alive:
            return

        self.x, self.y = position

    def set_loading_client(self, loading_type: int):

        if loading_type == Player.LOADING_TYPE_NONE:
            self.loading = loading_type
            self.load_time = 0
        elif loading_type == Player.LOADING_TYPE_EYE and self.loading == Player.LOADING_TYPE_NONE and self.eye_cooldown == 0:
            self.loading = loading_type
        elif loading_type == Player.LOADING_TYPE_MINE and self.loading == Player.LOADING_TYPE_NONE and self.mine_cooldown == 0:
            self.loading = loading_type

    def set_loading_server(self, loading_type: int):

        self.loading = loading_type
        if loading_type == Player.LOADING_TYPE_NONE:
            self.load_time = 0

    def add_eye_client(self):

        if not self.alive or self.eye_cooldown > 0:
            return None
        
        new_eye = Eye(self.id, self.x, self.y)

        self.eyes.append(new_eye)
        self.eye_cooldown = Eye.COOLDOWN_S

        return new_eye
    
    def add_eye_server(self, x: float, y: float):
        
        new_eye = Eye(self.id, x, y)

        self.eyes.append(new_eye)
        self.eye_cooldown = Eye.COOLDOWN_S

        return new_eye
    
    def add_mine_client(self):

        if not self.alive or len([mine for mine in self.mines if not mine.detonated]) == 1 or self.mine_cooldown > 0:
            return None
        
        new_mine = Mine(self.id, self.position)

        self.mines.append(new_mine)
        self.mine_cooldown = Mine.COOLDOWN_S

        return new_mine
    
    def add_mine_server(self, x: float, y: float):

        new_mine = Mine(self.id, (x, y))

        self.mines.append(new_mine)
        self.mine_cooldown = Mine.COOLDOWN_S

        return new_mine
    
    def add_missile_client(self, destination: Tuple[float, float]):

        if not self.alive or self.missile_cooldown > 0 or self.ammo <= 0:
            return None
        
        new_missile = Missile(self.id, self.position, destination)

        self.missiles.append(new_missile)
        self.missile_cooldown = Missile.COOLDOWN_S
        self.ammo -= 1

        return new_missile
    
    def add_missile_server(self, origin: Tuple[float, float], destination: Tuple[float, float]):

        new_missile = Missile(self.id, origin, destination)

        self.missiles.append(new_missile)
        self.missile_cooldown = Missile.COOLDOWN_S
        self.ammo -= 1

        return new_missile
    
    def kill(self):

        self.respawn_timer = Player.RESPAWN_TIME
        self.load_time = 0
    
    def render(self, surface: pygame.Surface, visibility_rects: List[pygame.Rect], color_scheme: ColorScheme):

        if self.alive and any(visibility_rect.colliderect(self.rect) for visibility_rect in visibility_rects):
            color = color_scheme.color_player_list[self.id % len(color_scheme.color_player_list)]
            pygame.draw.rect(surface, color, self.rect)
            if self.loading != Player.LOADING_TYPE_NONE:
                loading_sector(
                    surface,
                    pygame.Color(0, 0, 0, 50),
                    (round(self.x), round(self.y)),
                    20, 16,
                    self.load_time / self.loading_time_required
                )

    def render_fog(self, surface: pygame.Surface, fog_surface: pygame.Surface):

        new_fog_surface = fog_surface.copy()
        alpha_value = 255 - int(self.fog_brightness * 255)
        new_fog_surface.fill((0, 0, 0, alpha_value), special_flags=BLEND_RGBA_MAX)
        surface.blit(new_fog_surface, self.visibility_rect.topleft, special_flags=BLEND_RGBA_MIN)

    def update(self, gamestate, dt_s: float):

        if self.loading != Player.LOADING_TYPE_NONE:
            self.load_time += dt_s
            if self.loading == Player.LOADING_TYPE_EYE and self.load_time >= Eye.LOAD_TIME_S:
                self.add_eye_client()
                self.load_time = 0
                self.loading = Player.LOADING_TYPE_NONE
            elif self.loading == Player.LOADING_TYPE_MINE and self.load_time >= Mine.LOAD_TIME_S:
                self.add_mine_client()
                self.load_time = 0
                self.loading = Player.LOADING_TYPE_NONE

        self.eye_cooldown = max(0, self.eye_cooldown - dt_s)
        if len([mine for mine in self.mines if not mine.detonated]) < 1:
            self.mine_cooldown = max(0, self.mine_cooldown - dt_s)
        self.missile_cooldown = max(0, self.missile_cooldown - dt_s)

        for eye in self.eyes:
            eye.update(gamestate, dt_s)
        self.eyes = [eye for eye in self.eyes if eye.alive]

        for mine in self.mines:
            mine.update(gamestate, dt_s)
        self.mines = [mine for mine in self.mines if not mine.exploded]

        for missile in self.missiles:
            missile.update(gamestate, dt_s)
        self.missiles = [missile for missile in self.missiles if not missile.exploded]

        if not self.alive:
            self.fog_brightness = max(0, self.fog_brightness - dt_s * Player.FOG_BRIGHTNESS_CHANGE_RATE)
            self.respawn_timer = max(0, self.respawn_timer - dt_s)
            if self.respawn_timer == 0:
                self.x, self.y = self.spawnpoint
        else:
            self.fog_brightness = min(1, self.fog_brightness + dt_s * Player.FOG_BRIGHTNESS_CHANGE_RATE)