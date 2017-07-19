from builtins import object
from untwisted.network import Spin
from untwisted.event import CONNECT, CONNECT_ERR, WRITE
from untwisted import core
import socket

class Client(object):
    """
    Used to set up TCP clients.

    Diagram:
    
        WRITE -> Client -((), int:err)-> {**CONNECT, **CONNECT_ERR}
    """

    def __init__(self, spin):
        spin.add_map(WRITE, self.update)

    def update(self, spin):
        spin.del_map(WRITE, self.update)
        err = spin.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

        if err != 0:
            spin.drive(CONNECT_ERR, err)
        else:
            spin.drive(CONNECT)






