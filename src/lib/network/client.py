import sys
from threading import Thread, RLock
from src.utils.easysocket import *
from src.lib.network.protocol import *
from src.lib.app import PygameApp
from src.lib.gamestate import GameState
from src.lib.player import Player


class Client(EasySocket):

    def __init__(self, app: PygameApp, hostname: str):

        self.app = app
        self.hostname = hostname
        self.port = PORT

        super(Client, self).__init__()

        print(f'Connecting to {format_address((self.hostname, PORT))}')
        self.connected = self.connect(self.hostname, PORT)

        if not self.connected:
            print('Failed to connect to server!')
            sys.exit()

        self.gamestate = GameState(None)
        self.gamestate_lock = RLock()
        self.gamestate_updated = False
        self.kill_flag = False

        Thread(target=self.receive_loop, daemon=True).start()
        print('Connected as ', self.sockname)

        while not self.ready:
            pass

        self.app.initialize(self)

    @property
    def ready(self):

        return self.gamestate and self.gamestate.map_name is not None and self.sockname in self.gamestate.players

    def receive_loop(self):

        while True:

            data = self.receiveObject()
            if data is None: break

            msg_code, content = parse_message(data)
            if msg_code == MSG_CODE_MAP:
                self.set_gamestate_map_name(content)
            elif msg_code == MSG_CODE_PLAYER:
                peername, player_dict = content['peername'], content['player']
                incoming_player = Player.from_dict(player_dict)
                self.set_gamestate_player(peername, incoming_player)
            elif msg_code == MSG_CODE_KILL:
                print(f'Received kill notification')
                self.set_killed()

        print('Lost connection to server')

    def send_message(self, msg_code, content):
        self.sendObject(format_message(msg_code, content))

    def send_player_update(self, player: Player):
        self.sendObject(format_message(MSG_CODE_PLAYER, player.to_dict()))

    def send_kill_notification(self, killed_peername: int):
        self.sendObject(format_message(MSG_CODE_KILL, killed_peername))

    def get_gamestate(self):
        with self.gamestate_lock:
            if not self.gamestate_updated:
                return None
            self.gamestate_updated = False
            return self.gamestate
        
    def get_kill_flag(self):
        with self.gamestate_lock:
            if not self.kill_flag:
                return False
            self.kill_flag = False
            return True
        
    def set_gamestate_map_name(self, map_name: str):
        with self.gamestate_lock:
            self.gamestate.map_name = map_name
            self.gamestate_updated = True

    def set_gamestate_player(self, peername: str, incoming_player: Player):
        with self.gamestate_lock:
            self.gamestate.players[peername] = incoming_player
            self.gamestate_updated = True

    def set_killed(self):
        with self.gamestate_lock:
            self.kill_flag = True

    def reset_gamestate_updated(self):
        with self.gamestate_lock:
            self.gamestate_updated = False


if __name__ == '__main__':

    client = Client(PygameApp(), 'localhost')