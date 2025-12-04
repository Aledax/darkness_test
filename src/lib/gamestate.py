from src.lib.player import Player
from src.lib.map import MAPS

class GameState:

    def __init__(self, map_name: str, players: dict={}):

        self.players = players
        self.map_name = map_name

    @staticmethod
    def from_dict(data: dict):
        players = {}
        for peername, player_data in data['players'].items():
            player = Player.from_dict(player_data)
            players[peername] = player
        return GameState(data['map_name'], players)

    def to_dict(self):
        return {
            'players': {
                peername: player.to_dict() for peername, player in self.players.items()
            },
            'map_name': self.map_name
        }

    def add_player(self, client_peername: str):

        map = MAPS[self.map_name]
        self.players[client_peername] = Player(
            len(self.players),
            *map.spawn_positions[len(self.players) % len(map.spawn_positions)]
        )

    def update(self, dt_s: float):

        for player in self.players.values():
            player.update(self, dt_s)