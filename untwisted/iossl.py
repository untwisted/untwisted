from untwisted.network import xmap, zmap, spawn, Erase
from untwisted import iostd
from untwisted.event import get_event
from untwisted.event import WRITE, READ, CONNECT, CONNECT_ERR, CLOSE,      \
SEND_ERR, RECV_ERR, LOAD, SSL_SEND_ERR, SSL_RECV_ERR, SSL_CERTIFICATE_ERR, \
SSL_CONNECT_ERR, SSL_CONNECT
import socket
import ssl

class Stdin(iostd.Stdin):
    def update(self, spin):
        if not self.data: 
            self.process_queue(spin)

        try:
            size = spin.send(self.data)  
        except ssl.SSLError as excpt:
            spawn(spin, SSL_SEND_ERR, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])
        else:
            self.data = buffer(self.data, size)

class Stdout(iostd.Stdout):
    def update(self, spin):
        try:
            while True:
                self.process_data(spin)
        except ssl.SSLError as excpt:
            spawn(spin, SSL_RECV_ERR, spin, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])

class Handshake(object):
    """ 
    """

    def __init__(self, spin):
        xmap(spin, WRITE, self.do_handshake)

    def do_handshake(self, spin):
        """
        """

        try:
            spin.do_handshake()
        except ssl.CertificateError as excpt:
            spawn(spin, SSL_CERTIFICATE_ERR, excpt)
        except ssl.SSLWantReadError:
            pass
        except ssl.SSLWantWriteError:
            pass
        except ssl.SSLError as excpt:
            spawn(spin, SSL_CONNECT_ERR, excpt)
        else:
            spawn(spin, SSL_CONNECT)
            raise Erase

class Client(iostd.Client):
    def update(self, spin):
        iostd.Client.update(self, spin)
        Handshake(spin)


class Server(iostd.Server):
    def __init__(self, spin):
        xmap(spin, READ, self.update)

    def update(self, spin):
        pass





