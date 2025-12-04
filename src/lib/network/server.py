import sys
import time
from threading import Thread, RLock
from src.utils.easysocket import *
from src.lib.network.protocol import *
from src.lib.gamestate import GameState
from src.lib.eye import Eye
from src.lib.missile import Missile


class Server(ServerSocket):

    class ClientData:

        def __init__(self):

            self.name = None

    def __init__(self):

        self.hostname = 'localhost'
        self.port = PORT

        try:
            super(Server, self).__init__(self.hostname, self.port)
        except:
            print('Failed to bind to port!')
            sys.exit()

        print(f'Starting server on {format_address((self.hostname, self.port))}')

        self.client_datas = {}
        self.client_datas_lock = RLock()

        self.gamestate = GameState('sample_map')
        self.gamestate_lock = RLock()

        Thread(target=self.welcome_loop, daemon=True).start()
        Thread(target=self.gamestate_loop, daemon=True).start()

        input('Press Enter to stop the server\n')

    def welcome_loop(self):

        while True:
            client_sock = EasySocket(self.accept())
            print(f'New client: {client_sock.peername}')
            self.add_client(client_sock)
            Thread(target=self.client_loop, args=(client_sock,), daemon=True).start()

    def gamestate_loop(self):

        previous_time = time.perf_counter()

        while True:
            current_time = time.perf_counter()
            dt_s = current_time - previous_time

            with self.gamestate_lock:
                self.gamestate.update(dt_s)

            with self.client_datas_lock:
                for client_sock in self.client_datas.keys():
                    self.send_message(client_sock, MSG_CODE_GAMESTATE, self.gamestate.to_dict())

            previous_time = current_time

    def client_loop(self, client_sock: EasySocket):

        self.gamestate.add_player(client_sock.peername)

        while True:
            data = client_sock.receiveObject()
            if data is None: break

            msg_code, content = parse_message(data)
            if msg_code == MSG_CODE_POSITION:
                x, y = content['x'], content['y']
                with self.gamestate_lock:
                    player = self.gamestate.players[client_sock.peername]
                    player.move_to((x, y))
            if msg_code == MSG_CODE_LOAD:
                loading_type = content['loading']
                with self.gamestate_lock:
                    player = self.gamestate.players[client_sock.peername]
                    player.set_loading_server(loading_type)
            # elif msg_code == MSG_CODE_ADD_EYE:
            #     with self.gamestate_lock:
            #         player = self.gamestate.players[client_sock.peername]
            #         player.add_eye_server(content['x'], content['y'])
            #         print('Added eye for player', player.id)
            # elif msg_code == MSG_CODE_ADD_MINE:
            #     with self.gamestate_lock:
            #         player = self.gamestate.players[client_sock.peername]
            #         player.add_mine_server(*content['position'])
            #         print('Added mine for player', player.id)
            elif msg_code == MSG_CODE_ADD_MISSILE:
                with self.gamestate_lock:
                    player = self.gamestate.players[client_sock.peername]
                    player.add_missile_server(content['origin'], content['destination'])
                    print('Added missile for player', player.id)

        print(f'Lost client: {client_sock.peername}')
        self.del_client(client_sock)

    def add_client(self, client_sock: EasySocket):

        with self.client_datas_lock:
            self.client_datas[client_sock] = Server.ClientData()

    def del_client(self, client_sock: EasySocket):

        with self.client_datas_lock:
            self.client_datas.pop(client_sock)

    def send_message(self, client_sock: EasySocket, msg_code, content):

        client_sock.sendObject(format_message(msg_code, content))


if __name__ == '__main__':

    server = Server()