from untwisted.event import ACCEPT, READ, CLOSE, SSL_ACCEPT, WRITE, SSL_ACCEPT_ERR
from untwisted.dispatcher import Erase
from untwisted.errors import ACCEPT_ERR_CODE
from untwisted.client import install_basic_handles
from untwisted.network import SuperSocket, SuperSocketSSL
import socket
import ssl

class Server:
    """
    Used to set up TCP servers. It spawns ACCEPT_ERR or ACCEPT when new
    connections arise.

    """

    def __init__(self, ssock):
        ssock.add_map(READ, self.update)

    def update(self, ssock):
        while True:
            try:
                sock, addr = ssock.accept()
            except socket.error as excpt:
                if not excpt.args[0] in ACCEPT_ERR_CODE:
                    ssock.drive(CLOSE, excpt)
                break
            else:
                ssock.drive(ACCEPT, SuperSocket(sock))

class ServerHandshake:
    """ 
    """

    def __init__(self, server, ssock):
        self.server = server
        ssock.add_map(WRITE, self.do_handshake)

    def do_handshake(self, ssock):
        """
        """

        try:
            ssock.do_handshake()
        except ssl.SSLWantReadError:
            pass
        except ssl.SSLWantWriteError:
            pass
        except socket.error as excpt:
            self.server.drive(SSL_ACCEPT_ERR, ssock, excpt)
        else:
            self.server.drive(SSL_ACCEPT, ssock)
            raise Erase

class ServerSSL:
    def __init__(self, ssock):
        ssock.add_map(READ, self.update)

    def update(self, ssock):
        while True:
            try:
                sock, addr = ssock.accept()
            except socket.error as excpt:
                if not excpt.args[0] in ACCEPT_ERR_CODE:
                    ssock.drive(CLOSE, excpt)
                break
            ServerHandshake(ssock, SuperSocketSSL(sock))

handles_wrapper = lambda server, ssock: install_basic_handles(ssock)
def create_server(addr, port, backlog):
    """
    """

    server = SuperSocket()
    server.bind((addr, port))
    server.listen(backlog)
    Server(server)
    server.add_map(ACCEPT, handles_wrapper)
    return server

def create_server_ssl(addr, port, backlog):
    """
    """

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((addr, port))
    server.listen(backlog)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_default_certs()

    wrap = context.wrap_socket(server, 
    do_handshake_on_connect=False, server_side=True)

    sserver = SuperSocketSSL(wrap)
    ServerSSL(sserver)

    sserver.add_map(SSL_ACCEPT, handles_wrapper)
    return sserver

