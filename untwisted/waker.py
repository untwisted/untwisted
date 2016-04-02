from socket import socket, AF_INET, SOCK_STREAM
from untwisted.network import Spin, xmap
from untwisted.event import READ
from threading import Lock

class Waker(object):
    MAX_SIZE = 6028
    def __init__(self):
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)

        client = Spin()
        client.connect_ex(server.getsockname())

        def consume(spin):
            spin.recv(self.MAX_SIZE)

        xmap(client, READ, consume)

        self.con, addr  = server.accept()
        self.lock       = Lock()

    def wake_up(self):
        with self.lock:
            self.con.send(' ')
    
waker = Waker()



