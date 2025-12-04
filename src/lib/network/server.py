import sys
import time
from threading import Thread, RLock
from src.utils.easysocket import *
from src.lib.network.protocol import *
from src.lib.gamestate import GameState
from src.lib.player import Player
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

        pass

        # previous_time = time.perf_counter()

        # while True:
        #     current_time = time.perf_counter()
        #     dt_s = current_time - previous_time

        #     with self.gamestate_lock:
        #         self.gamestate.update(dt_s)

        #     with self.client_datas_lock:
        #         for client_sock in self.client_datas.keys():
        #             self.send_message(client_sock, MSG_CODE_GAMESTATE, self.gamestate.to_dict())

        #     previous_time = current_time

    def client_loop(self, client_sock: EasySocket):

        self.gamestate.add_player(client_sock.peername)
        self.send_map(client_sock)
        self.send_player_update(client_sock, self.gamestate.players[client_sock.peername])

        while True:
            data = client_sock.receiveObject()
            if data is None: break

            msg_code, content = parse_message(data)
            if msg_code == MSG_CODE_PLAYER:
                incoming_player = Player.from_dict(content)
                with self.gamestate_lock:
                    self.gamestate.players[client_sock.peername] = incoming_player
                with self.client_datas_lock:
                    for other_sock in self.client_datas:
                        if other_sock != client_sock:
                            self.send_message(other_sock, MSG_CODE_PLAYER, {
                                'peername': client_sock.peername,
                                'player': incoming_player.to_dict()
                                })
            elif msg_code == MSG_CODE_KILL:
                killed_peername = content
                killed_client_sock = [sock for sock in self.client_datas.keys() if sock.peername == killed_peername][0]
                with self.gamestate_lock:
                    self.send_message(killed_client_sock, MSG_CODE_KILL, {})

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

    def send_map(self, client_sock: EasySocket):

        client_sock.sendObject(format_message(MSG_CODE_MAP, self.gamestate.map_name))

    def send_player_update(self, client_sock: EasySocket, player: Player):

        client_sock.sendObject(format_message(MSG_CODE_PLAYER, {
            'peername': client_sock.peername,
            'player': player.to_dict()
            }))


if __name__ == '__main__':

    server = Server()