from untwisted.network import xmap, zmap, spawn, Erase
from untwisted import iostd
from untwisted.event import WRITE, READ, CONNECT, CONNECT_ERR, CLOSE, SEND_ERR, RECV_ERR, LOAD
import socket
import ssl

class Stdin(iostd.Stdin):
    def update(self, spin):
        try:
            self.send_data(spin)
        except ssl.SSLWantWriteError:
            pass
        except ssl.SSLError as excpt:
            spawn(spin, SEND_ERR, excpt.errno)
        except socket.error as excpt:
            self.handle_socket_error(excpt.args[0])

class Stdout(iostd.Stdout):
    def update(self, spin):
        try:
            self.recv_data(spin)
        except ssl.SSLWantReadError:
            pass
        except ssl.SSLError:
            spawn(spin, RECV_ERR, excpt.errno)
        except socket.error:
            self.handle_socket_error(excpt.args[0])

    def recv_data(self, spin):
        while True:
            iostd.Stdout.recv_data(self, spin)
            
class Client(iostd.Client):
    def update(self, spin):
        err = spin.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

        if err != 0:
            spawn(spin, CONNECT_ERR, err)
        else:
            Handshake(spin)
            raise Erase

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
        except ssl.CertificateError:
            spawn(spin, CONNECT_ERR, excpt.errno)
        except ssl.SSLWantReadError:
            pass
        except ssl.SSLWantWriteError:
            pass
        except ssl.SSLError:
            spawn(spin, CONNECT_ERR, excpt.errno)
        else:
            spawn(spin, CONNECT)
            raise Erase

class Server(iostd.Server):
    def __init__(self, spin):
        xmap(spin, READ, self.update)

    def update(self, spin):
        pass

    def handle_ssl_error(self, spin, excpt):
        pass

