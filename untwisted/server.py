from builtins import object
from untwisted.errors import ACCEPT_ERR_CODE
from untwisted.event import ACCEPT, ACCEPT_ERR, READ
from untwisted.network import Spin
import socket

class Server(object):
    """
    Used to set up TCP servers.

    READ -> Server -(Spin:client, int:err)-> {ACCEPT, ACCEPT_ERR}
    """

    def __init__(self, spin, wrap = lambda sock: Spin(sock)):
        spin.add_map(READ, self.update)
        self.wrap = wrap

    def update(self, spin):
        while True:
            try:
                sock, addr = spin.accept()
            except socket.error as excpt:
                err = excpt.args[0]
                if not err in ACCEPT_ERR_CODE:
                    spin.drive(ACCEPT_ERR, err)
                else:
                    break
            else:
                spin.drive(ACCEPT, self.wrap(sock))


