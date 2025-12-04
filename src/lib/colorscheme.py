import pygame
from pygame.locals import *
from typing import List


class ColorScheme:

    def __init__(self,
                 color_bg: pygame.Color,
                 color_wall: pygame.Color,
                 color_player_list: List[pygame.Color]):

        self.color_bg = color_bg
        self.color_wall = color_wall
        self.color_player_list = color_player_list

    # @staticmethod
    # def from_dict(data: dict):
    #     return ColorScheme(
    #         color_bg=pygame.Color(*data['color_bg']),
    #         color_wall=pygame.Color(*data['color_wall']),
    #         color_player=pygame.Color(*data['color_player'])
    #     )
    
    # def to_dict(self):
    #     return {
    #         'color_bg': (self.color_bg.r, self.color_bg.g, self.color_bg.b, self.color_bg.a),
    #         'color_wall': (self.color_wall.r, self.color_wall.g, self.color_wall.b, self.color_wall.a),
    #         'color_player': (self.color_player.r, self.color_player.g, self.color_player.b, self.color_player.a)
    #     }

        
SAMPLE_COLOR_SCHEME = ColorScheme(
    color_bg=pygame.Color(65, 82, 84),
    color_wall=pygame.Color(30, 61, 65),
    color_player_list=[
        pygame.Color(163, 203, 61),
        pygame.Color(239, 83, 80),
        pygame.Color(255, 202, 40),
        pygame.Color(66, 165, 245)
    ]
)