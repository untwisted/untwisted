from untwisted.event import CLOSE, RECV_ERR, READ, LOAD, SSL_RECV_ERR
from untwisted.errors import CLOSE_ERR_CODE, RECV_ERR_CODE
import socket
import ssl

class SockReader:
    """
    Used to read data through a Spin instance.
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

        if not data: 
            raise socket.error('')
        spin.drive(LOAD, data)

    def process_error(self, spin, excpt):
        if excpt.args[0] in RECV_ERR_CODE:
            spin.drive(RECV_ERR, excpt)
        elif excpt.args[0] in CLOSE_ERR_CODE: 
            spin.drive(CLOSE, excpt)
        else:
            raise excpt

class SockReaderSSL(SockReader):
    def update(self, spin):
        try:
            self.process_data(spin)
        except ssl.SSLWantReadError as excpt:
            spin.drive(SSL_RECV_ERR, spin, excpt)
        except ssl.SSLWantWriteError as excpt:
            spin.drive(SSL_RECV_ERR, spin, excpt)
        except ssl.SSLError as excpt:
            spin.drive(CLOSE, spin, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt)






