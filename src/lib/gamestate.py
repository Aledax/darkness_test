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

    def update_server(self, dt_s: float):

        pass
        # for player in self.players.values():
        #     player.update(self, dt_s)

    # def update_client_and_get_hits(self, sockname: str, dt_s: float):

    #     if sockname in self.players:
    #         return self.players[sockname].update_and_get_hits(self, dt_s)

    def integrate_incoming_server_gamestate(self, sockname: str, incoming_gamestate: 'GameState'):

        new_players = {}
        if sockname in self.players:
            new_players[sockname] = self.players[sockname]
        for peername, incoming_player in incoming_gamestate.players.items():
            new_players[peername] = incoming_player
        self.players = new_players