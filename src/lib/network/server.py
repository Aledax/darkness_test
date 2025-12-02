import sys
from threading import Thread, RLock
from utils.easysocket import *


class Server(ServerSocket):

    class ClientData:

        def __init__(self):

            self.name = None

    def __init__(self):

        self.hostname = '0.0.0.0'
        self.port = PORT

        try:
            super(Server, self).__init__(self.hostname, self.port)
        except:
            print('Failed to bind to port!')
            sys.exit()

        print(f'Starting server on {format_address((self.hostname, self.port))}')

        self.client_datas = {}
        self.client_datas_lock = RLock()

        Thread(target=self.welcome_loop, daemon=True).start()

        input('Press Enter to stop the server')

    def welcome_loop(self):

        while True:
            client_sock = EasySocket(self.accept())
            print(f'New client: {client_sock.peername}')
            self.add_client(client_sock)
            Thread(target=self.client_loop, args=(client_sock,), daemon=True).start()

    def client_loop(self, client_sock: EasySocket):

        while True:
            data = client_sock.receiveObject()
            if data is None: break

            # Validate message?

        print(f'Lost client: {client_sock.peername}')
        self.del_client(client_sock)

    def add_client(self, client_sock: EasySocket):

        with self.client_datas_lock:
            self.client_datas[client_sock] = Server.ClientData()

    def del_client(self, client_sock: EasySocket):

        with self.client_datas_lock:
            self.client_datas.pop(client_sock)


if __name__ == '__main__':

    server = Server()