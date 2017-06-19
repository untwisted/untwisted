from untwisted.network import SSL, xmap, zmap, spawn, Erase
from untwisted.iostd import DumpStr, DumpFile, Stdout, Stdin, Client, Server, lose
from untwisted.event import get_event
from untwisted.event import WRITE, READ, CONNECT, CONNECT_ERR, CLOSE,      \
SEND_ERR, RECV_ERR, LOAD, SSL_SEND_ERR, SSL_RECV_ERR, SSL_CERTIFICATE_ERR, \
SSL_CONNECT_ERR, SSL_CONNECT
import socket
import ssl

class DumpStrSSL(DumpStr):
    def process(self, spin):
        try:
            size = spin.send(self.data)  
        except ssl.SSLError as excpt:
            spawn(spin, SSL_SEND_ERR, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])
        else:
            self.data = buffer(self.data, size)

class DumpFileSSL(DumpStrSSL, DumpFile):
    pass

class StdinSSL(Stdin):
    def dump(self, data):
        self.start()
        data = DumpStr(data)
        self.queue.append(data)

    def dumpfile(self, fd):
        self.start()
        fd = DumpFile(fd)
        self.queue.append(fd)

class StdoutSSL(Stdout):
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

class ClientSSL(Client):
    def update(self, spin):
        Client.update(self, spin)
        Handshake(spin)

class ServerSSL(Server):
    def __init__(self, spin):
        xmap(spin, READ, self.update)

    def update(self, spin):
        pass

def install_ssl_handles(con):
    StdinSSL(con)
    StdoutSSL(con)
    xmap(con, CLOSE, lambda con, err: lose(con))

def create_client_ssl(addr, port):
    sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    con     = SSL(context.wrap_socket(sock, 
    do_handshake_on_connect=False, server_hostname=addr))

    con.connect_ex((addr, port))

    ClientSSL(con)
    xmap(con, SSL_CONNECT, install_ssl_handles)
    xmap(con, SSL_CONNECT_ERR, lambda con, err: lose(err))
    xmap(con, SSL_CERTIFICATE_ERR, lambda con, err: lose(err))
    return con

def create_server_ssl():
    pass





