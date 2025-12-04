import sys
from threading import Thread, RLock
from src.utils.easysocket import *
from src.lib.network.protocol import *
from src.lib.app import PygameApp
from src.lib.gamestate import GameState


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

        self.gamestate = None
        self.gamestate_lock = RLock()
        self.gamestate_updated = False

        Thread(target=self.receive_loop, daemon=True).start()
        print('Connected as ', self.sockname)

        while self.gamestate is None:
            pass

        self.app.initialize(self)

    def receive_loop(self):

        while True:

            data = self.receiveObject()
            if data is None: break

            msg_code, content = parse_message(data)
            if msg_code == MSG_CODE_GAMESTATE:
                self.set_gamestate(GameState.from_dict(content))

        print('Lost connection to server')

    def send_message(self, msg_code, content):
        
        self.sendObject(format_message(msg_code, content))

    def get_gamestate(self):
        with self.gamestate_lock:
            if not self.gamestate_updated:
                return None
            return self.gamestate
        
    def set_gamestate(self, gamestate: GameState):
        with self.gamestate_lock:
            self.gamestate = gamestate
            self.gamestate_updated = True

    def reset_gamestate_updated(self):
        with self.gamestate_lock:
            self.gamestate_updated = False


if __name__ == '__main__':

    client = Client(PygameApp(), 'localhost')