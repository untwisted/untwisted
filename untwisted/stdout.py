from builtins import object
from untwisted.event import CLOSE, RECV_ERR, READ, LOAD
from untwisted.errors import CLOSE_ERR_CODE, RECV_ERR_CODE
import socket

class Stdout(object):
    """
    Used to read data through a Spin instance.

    Diagram:
    
        READ -> Stdout -(int:err, int:err, str:data)-> {**CLOSE, RECV_ERR, LOAD}
    """
    
    SIZE = 1024 * 124

    def __init__(self, spin):
        spin.add_map(READ, self.update)

    def update(self, spin):
        """
        """

        try:
            self.process_data(spin)
        except socket.error as excpt:
            self.process_error(spin, excpt)

    def process_data(self, spin):
        data = spin.recv(self.SIZE)

        # It has to raise the error here
        # otherwise it CLOSE gets spawned
        # twice from SSLStdout.
        if not data: raise socket.error('')
        spin.drive(LOAD, data)

    def process_error(self, spin, excpt):
        if excpt.args[0] in RECV_ERR_CODE:
            spin.drive(RECV_ERR, excpt)
        elif excpt.args[0] in CLOSE_ERR_CODE: 
            spin.drive(CLOSE, excpt)
        else:
            raise excpt



