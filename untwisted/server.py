from untwisted.event import ACCEPT, ACCEPT_ERR, READ
from untwisted.errors import ACCEPT_ERR_CODE
from untwisted.client import install_basic_handles
from untwisted.network import SuperSocket
import socket

class Server:
    """
    Used to set up TCP servers.

    """

    def __init__(self, ssock, wrap = lambda sock: SuperSocket(sock)):
        ssock.add_map(READ, self.update)
        self.wrap = wrap

    def update(self, ssock):
        while True:
            try:
                sock, addr = ssock.accept()
            except socket.error as excpt:
                if not excpt.args[0] in ACCEPT_ERR_CODE:
                    ssock.drive(ACCEPT_ERR, excpt.args[0])
                else:
                    break
            else:
                ssock.drive(ACCEPT, self.wrap(sock))

def create_server(addr, port, backlog):
    """
    """

    server = SuperSocket()
    server.bind((addr, port))
    server.listen(backlog)
    Server(server)
    server.add_map(ACCEPT, lambda server, ssock: install_basic_handles(ssock))
    return server


