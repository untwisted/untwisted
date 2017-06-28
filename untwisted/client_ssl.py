from untwisted.network import SSL, xmap, zmap, spawn
from untwisted.client import Client
from untwisted.exceptions import Erase
from untwisted.event import WRITE, SSL_CERTIFICATE_ERR, \
SSL_CONNECT_ERR, SSL_CONNECT
import socket
import ssl

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



