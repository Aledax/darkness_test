import pygame
from pygame.locals import *
from typing import List, Tuple
from src.lib.wall import Wall
from src.lib.colorscheme import ColorScheme, SAMPLE_COLOR_SCHEME
from src.lib.player import Player


class Map:

    def __init__(self,
                 size: Tuple[int],
                 walls: List[Wall],
                 spawn_positions: List[tuple],
                #  flag_positions: List[tuple],
                #  ammo_positions: List[tuple],
                 color_scheme: ColorScheme):

        self.size = size
        self.walls = walls
        self.spawn_positions = spawn_positions
        # self.flag_positions = flag_positions
        # self.ammo_positions = ammo_positions
        self.color_scheme = color_scheme

        outside_border_thickness = 100
        outside_border_walls = [
            Wall(-outside_border_thickness, -outside_border_thickness, size[0] + 2 * outside_border_thickness, outside_border_thickness),
            Wall(-outside_border_thickness, size[1], size[0] + 2 * outside_border_thickness, outside_border_thickness),
            Wall(-outside_border_thickness, -outside_border_thickness, outside_border_thickness, size[1] + 2 * outside_border_thickness),
            Wall(size[0], -outside_border_thickness, outside_border_thickness, size[1] + 2 * outside_border_thickness)
        ]
        self.walls.extend(outside_border_walls)

    # @staticmethod
    # def from_dict(data: dict):

    #     walls = [Wall.from_dict(wall_data) for wall_data in data['walls']]
    #     spawn_positions = data['spawn_positions']
    #     color_scheme = ColorScheme.from_dict(data['color_scheme'])
    #     return Map(walls, spawn_positions, color_scheme)

    # def to_dict(self):

    #     return {
    #         'walls': [
    #             wall.to_dict() for wall in self.walls
    #         ],
    #         'spawn_positions': self.spawn_positions,
    #         'color_scheme': self.color_scheme.to_dict()
    #     }

    def render(self, bg_surface: pygame.Surface, mg_surface: pygame.Surface):

        bg_surface.fill(self.color_scheme.color_bg)

        for wall in self.walls:
            wall.render(mg_surface, self.color_scheme.color_wall)

    def resolve_player_wall_collisions(self, player: Player, direction: tuple):

        for wall in self.walls:
            wall.resolve_player_collision(player, direction)


RESOLUTION = (600, 600)
WALL_BORDER_THICKNESS = 40
SAMPLE_MAP = Map(
    RESOLUTION,
    [
        Wall(0, 0, RESOLUTION[0], WALL_BORDER_THICKNESS),
        Wall(0, WALL_BORDER_THICKNESS, WALL_BORDER_THICKNESS, RESOLUTION[1] - 2 * WALL_BORDER_THICKNESS),
        Wall(RESOLUTION[0] - WALL_BORDER_THICKNESS, WALL_BORDER_THICKNESS, WALL_BORDER_THICKNESS, RESOLUTION[1] - 2 * WALL_BORDER_THICKNESS),
        Wall(0, RESOLUTION[1] - WALL_BORDER_THICKNESS, RESOLUTION[0], WALL_BORDER_THICKNESS),

        Wall(200, 200, 50, 50),
        Wall(350, 350, 50, 50),
        Wall(200, 350, 50, 50),
        Wall(350, 200, 50, 50)
    ],
    [
        (100, 100),
        (500, 500),
        (100, 500),
        (500, 100)
    ],
    SAMPLE_COLOR_SCHEME
)

MAPS = {
    'sample_map': SAMPLE_MAP
}