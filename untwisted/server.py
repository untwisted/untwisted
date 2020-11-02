from untwisted.event import ACCEPT, ACCEPT_ERR, READ

from untwisted.errors import ACCEPT_ERR_CODE

from untwisted.client import install_basic_handles
from untwisted.network import Spin
import socket

class Server:
    """
    Used to set up TCP servers.

    """

    def __init__(self, spin, wrap = lambda sock: Spin(sock)):
        spin.add_map(READ, self.update)
        self.wrap = wrap

    def update(self, spin):
        while True:
            try:
                sock, addr = spin.accept()
            except socket.error as excpt:
                if not excpt.args[0] in ACCEPT_ERR_CODE:
                    spin.drive(ACCEPT_ERR, excpt.args[0])
                else:
                    break
            else:
                spin.drive(ACCEPT, self.wrap(sock))

def create_server(addr, port, backlog):
    """
    Set up a TCP server and installs the basic handles Stdin, Stdout in the
    clients.

    Example:    

    def send_data(server, client):
        # No need to install Stdin or Stdout.
        client.dump('foo bar!')

    server = create_server('0.0.0.0', 1024, 50)
    xmap(server, on_accept, send_data)
    """

    server = Spin()
    server.bind((addr, port))
    server.listen(backlog)
    Server(server)
    server.add_map(ACCEPT, lambda server, spin: install_basic_handles(spin))
    return server


