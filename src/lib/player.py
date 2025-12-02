import math
import pygame
from pygame.locals import *
from src.utils.pygameutils import *


class Player:

    RADIUS = 10
    SPEED = 200
    
    def __init__(self, x: float, y: float):

        self.x = x
        self.y = y
        
        self.r = Player.RADIUS
        self.r_squared = self.r ** 2

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
    
    def move_by(self, angle_radians, dt):
        new_x = self.x + math.cos(angle_radians) * Player.SPEED * dt
        new_y = self.y + math.sin(angle_radians) * Player.SPEED * dt

        self.x, self.y = new_x, new_y

    def move_to(self, position):
        self.x, self.y = position    
    
    def render(self, surface: pygame.Surface, color: pygame.Color):
        # aacircle_filled(surface, round(self.x), round(self.y), Player.RADIUS, color)
        pygame.draw.rect(surface, color, self.rect)