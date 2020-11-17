from untwisted.event import CONNECT, CONNECT_ERR, WRITE, CLOSE, CLOSE_ERR, \
SSL_CERTIFICATE_ERR, SSL_CONNECT_ERR, SSL_CONNECT

from untwisted.dispatcher import Erase
from untwisted.sock_writer import SockWriter, SockWriterSSL
from untwisted.sock_reader import SockReader, SockReaderSSL
from untwisted.network import Spin
from untwisted.network import SSL

import socket
import ssl

class Client:
    """
    Used to set up TCP clients.

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

class Handshake:
    """ 
    """

    def __init__(self, spin):
        spin.add_map(WRITE, self.do_handshake)

    def do_handshake(self, spin):
        """
        """

        try:
            spin.do_handshake()
        except ssl.CertificateError as excpt:
            spin.drive(SSL_CERTIFICATE_ERR, excpt)
        except ssl.SSLWantReadError:
            pass
        except ssl.SSLWantWriteError:
            pass
        except socket.error as excpt:
            # When it happens then it should spawn SSL_CONNECT_ERR.
            spin.drive(SSL_CONNECT_ERR, excpt)
        except ssl.SSLError as excpt:
            spin.drive(SSL_CONNECT_ERR, excpt)
        else:
            spin.drive(SSL_CONNECT)
            raise Erase

class ClientSSL:
    def __init__(self, spin):
        Client(spin)
        spin.add_map(CONNECT, self.update)

    def update(self, spin):
        spin.del_map(CONNECT, self.update)
        Handshake(spin)

def lose(spin):
    """
    It is used to close TCP connection and unregister
    the Spin instance from untwisted reactor.

    """

    # First unregister it otherwise it raises an error
    # due to the fd being closed when unregistering off
    # epoll.
    spin.destroy()

    try:
        spin.close()
    except OSError as excpt:
        spin.drive(CLOSE_ERR, excpt.args[0])

def put(spin, data):
    """
    A handle used to serialize arguments of events.
    
    xmap(con, LOAD, put)
    """

    print(data)

def install_basic_handles(spin):
    """
    """

    SockWriter(spin)
    SockReader(spin)
    spin.add_map(CLOSE, lambda spin, err: lose(spin))

def create_client(addr, port):
    """
    Set up a TCP client and installs the basic handles Stdin, Stdout.

    def send_data(client):
        client.dump('GET / HTTP/1.1\r\n')
        xmap(client, LOAD, iostd.put)

    client = create_client('www.google.com.br', 80)
    xmap(client, CONNECT, send_data)
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # First attempt to connect otherwise it leaves
    # an unconnected spin instance in the reactor.
    sock.connect_ex((addr, port))

    spin = Spin(sock)
    Client(spin)
    spin.add_map(CONNECT, install_basic_handles)
    spin.add_map(CONNECT_ERR, lambda con, err: lose(con))
    return spin

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
    # an unconnected spin instance in the reactor.
    wrap.connect_ex((addr, port))
    con = SSL(wrap)

    ClientSSL(con)
    con.add_map(SSL_CONNECT, install_ssl_handles)
    con.add_map(SSL_CONNECT_ERR, lambda con, err: lose(con))
    con.add_map(CONNECT_ERR, lambda con, err: lose(con))
    con.add_map(SSL_CERTIFICATE_ERR, lambda con, err: lose(con))
    return con
