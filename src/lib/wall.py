import pygame
from pygame.locals import *
from src.lib.player import Player
from src.utils.nputils import *

class Wall:

    def __init__(self, left, top, width, height):

        self.left = left
        self.top = top
        self.width = width
        self.height = height

    @property
    def right(self):
        return self.left + self.width
    
    @property
    def bottom(self):
        return self.top + self.height
    
    @property
    def rect(self):
        return pygame.Rect(self.left, self.top, self.width, self.height)
    
    # @staticmethod
    # def from_dict(data: dict):
    #     return Wall(data['left'], data['top'], data['width'], data['height'])

    # def to_dict(self):
    #     return {
    #         'left': self.left,
    #         'top': self.top,
    #         'width': self.width,
    #         'height': self.height
    #     }
    
    def render(self, surface: pygame.Surface, color: pygame.Color):

        pygame.draw.rect(surface, color, self.rect)

    def resolve_player_collision(self, player: Player, direction: tuple):

        if not player.rect.colliderect(self.rect):
            return

        rectify_direction = None

        if direction == (1, 0):
            rectify_direction = 'left'
        elif direction == (-1, 0):
            rectify_direction = 'right'
        elif direction == (0, 1):
            rectify_direction = 'top'
        elif direction == (0, -1):
            rectify_direction = 'bottom'
        elif direction == (1, 1):
            if player.right - self.left < player.bottom - self.top:
                rectify_direction = 'left'
            else:
                rectify_direction = 'top'
        elif direction == (-1, 1):
            if self.right - player.left < player.bottom - self.top:
                rectify_direction = 'right'
            else:
                rectify_direction = 'top'
        elif direction == (1, -1):
            if player.right - self.left < self.bottom - player.top:
                rectify_direction = 'left'
            else:
                rectify_direction = 'bottom'
        elif direction == (-1, -1):
            if self.right - player.left < self.bottom - player.top:
                rectify_direction = 'right'
            else:
                rectify_direction = 'bottom'

        if rectify_direction == 'left':
            player.move_to((self.left - player.r, player.y))
        elif rectify_direction == 'right':
            player.move_to((self.right + player.r, player.y))
        elif rectify_direction == 'top':
            player.move_to((player.x, self.top - player.r))
        elif rectify_direction == 'bottom':
            player.move_to((player.x, self.bottom + player.r))
        else:
            print('Error resolving player collision')