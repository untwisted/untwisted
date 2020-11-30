from untwisted.event import ACCEPT, ACCEPT_ERR, READ, CLOSE, SSL_ACCEPT
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
                else:
                    break
            ssock.drive(ACCEPT, SuperSocket(sock))

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
                else:
                    break
            except ssl.SSLWantReadError:
                pass
            except ssl.SSLWantWriteError:
                pass
            except ssl.SSLError as excpt:
                ssock.drive(CLOSE, excpt)
            else:
                ssock.drive(SSL_ACCEPT, SuperSocketSSL(sock))

def create_server(addr, port, backlog):
    """
    """

    server = SuperSocket()
    server.bind((addr, port))
    server.listen(backlog)
    Server(server)
    server.add_map(ACCEPT, lambda server, ssock: install_basic_handles(ssock))
    return server

def create_server_ssl(addr, port, backlog, certchain):
    """
    """

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((addr, port))
    server.listen(backlog)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(*certchain)
    
    wrap = context.wrap_socket(server, 
    do_handshake_on_connect=False, server_side=True)

    sserver = SuperSocketSSL(wrap)
    ServerSSL(sserver)

    sserver.add_map(SSL_ACCEPT, lambda server, ssock: install_basic_handles(ssock))
    return sserver

