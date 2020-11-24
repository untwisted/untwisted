from untwisted.event import CONNECT, CONNECT_ERR, WRITE, CLOSE, CLOSE_ERR, \
SSL_CERTIFICATE_ERR, SSL_CONNECT_ERR, SSL_CONNECT

from untwisted.dispatcher import Erase
from untwisted.sock_writer import SockWriter, SockWriterSSL
from untwisted.sock_reader import SockReader, SockReaderSSL
from untwisted.network import SuperSocket
from untwisted.network import SSL

import socket
import ssl

class Client:
    """
    Used to set up TCP clients.

    """

    def __init__(self, ssock):
        ssock.add_map(WRITE, self.update)

    def update(self, ssock):
        ssock.del_map(WRITE, self.update)
        err = ssock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

        if err != 0:
            ssock.drive(CONNECT_ERR, err)
        else:
            ssock.drive(CONNECT)

class Handshake:
    """ 
    """

    def __init__(self, ssock):
        ssock.add_map(WRITE, self.do_handshake)

    def do_handshake(self, ssock):
        """
        """

        try:
            ssock.do_handshake()
        except ssl.CertificateError as excpt:
            ssock.drive(SSL_CERTIFICATE_ERR, excpt)
        except ssl.SSLWantReadError:
            pass
        except ssl.SSLWantWriteError:
            pass
        except socket.error as excpt:
            # When it happens then it should spawn SSL_CONNECT_ERR.
            ssock.drive(SSL_CONNECT_ERR, excpt)
        except ssl.SSLError as excpt:
            ssock.drive(SSL_CONNECT_ERR, excpt)
        else:
            ssock.drive(SSL_CONNECT)
            raise Erase

class ClientSSL:
    def __init__(self, ssock):
        Client(ssock)
        ssock.add_map(CONNECT, self.update)

    def update(self, ssock):
        ssock.del_map(CONNECT, self.update)
        Handshake(ssock)

def lose(ssock):
    """
    It is used to close TCP connection and unregister
    the SuperSocket instance from untwisted reactor.

    """

    # First unregister it otherwise it raises an error
    # due to the fd being closed when unregistering off
    # epoll.

    ssock.destroy()
    ssock.close()

def put(ssock, data):
    """
    """

    print(data)

def install_basic_handles(ssock):
    """
    """

    SockWriter(ssock)
    SockReader(ssock)
    ssock.add_map(CLOSE, lambda ssock, err: lose(ssock))

def create_client(addr, port):
    """
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # First attempt to connect otherwise it leaves
    # an unconnected ssock instance in the reactor.
    sock.connect_ex((addr, port))

    ssock = SuperSocket(sock)
    Client(ssock)
    ssock.add_map(CONNECT, install_basic_handles)
    ssock.add_map(CONNECT_ERR, lambda con, err: lose(con))
    return ssock

def install_ssl_handles(con):
    SockWriterSSL(con)
    SockReaderSSL(con)
    con.add_map(CLOSE, lambda con, err: lose(con))

def create_client_ssl(addr, port):
    sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    wrap    = context.wrap_socket(sock, 
    do_handshake_on_connect=False, server_hostname=addr)

    # First attempt to connect otherwise it leaves
    # an unconnected ssock instance in the reactor.
    wrap.connect_ex((addr, port))
    con = SSL(wrap)

    ClientSSL(con)
    con.add_map(SSL_CONNECT, install_ssl_handles)
    con.add_map(SSL_CONNECT_ERR, lambda con, err: lose(con))
    con.add_map(CONNECT_ERR, lambda con, err: lose(con))
    con.add_map(SSL_CERTIFICATE_ERR, lambda con, err: lose(con))
    return con
