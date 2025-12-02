from threading import Thread
from src.utils.easysocket import *
from src.lib.network.protocol import *


class Client(EasySocket):

    def __init__(self, hostname):

        self.hostname = hostname
        self.port = PORT

        super(Client, self).__init__()

        print(f'Connecting to {format_address((self.hostname, PORT))}')
        self.connected = self.connect(self.hostname, PORT)

        Thread(target=self.receive_loop, daemon=True).start()

    def receive_loop(self):

        while True:

            data = self.receiveObject()
            if data is None: break

            # Validate message?

        print('Lost connection to server')

    def send_message(self, msg_code, content):
        
        self.sendObject(format_message(msg_code, content))